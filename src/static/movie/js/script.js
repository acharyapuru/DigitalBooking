document.addEventListener('DOMContentLoaded', function() {
    // Start the timer
    const timerInterval = setInterval(updateTimer, 1000);

    const movieInfo = document.getElementById('movie-info');
    if (!movieInfo) {
        return;
    }
    const movieSlug = movieInfo.dataset.movie ;
    const theaterSlug = movieInfo.dataset.theater ;
    const showTime = movieInfo.dataset.showtime ;

    const connSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/movie/' + movieSlug + '/' + theaterSlug + '/' + showTime + '/'
    );

    connSocket.onopen = function(e) {
        console.log('Connection established');
    };

    let timeLeft = 300; // 10 minutes in seconds
    const timerDisplay = document.getElementById("timer");

    // Function to update the timer
    function updateTimer() {
        if (!timerDisplay) {
            return;
        }
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerDisplay.textContent = "Time's up! Please reload page to book tickets.";
            closeWebSocketConnection(connSocket); // Call your function to close the WebSocket connection
        } else {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            timeLeft--;
        }
    }

    connSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const rows = data.data;

        console.log(data);

        const source = data.source;

        if (source === 'movie.seats') {
            mapSeats(connSocket, rows, showTime);
        } else if (source === 'movie.seat_update') {
            updateSeat(data.data);
        }
    };

    // Function to close WebSocket connection
    function closeWebSocketConnection(socket) {
        if (socket) {
            socket.close();
            console.log("WebSocket connection closed.");
        }
    }

    // Function to map seats
    function mapSeats(connSocket, rows, showTime) {
        const seatContainer = document.getElementById('seat-container');
        seatContainer.innerHTML = '';

        for (const i in rows) {
            const row = document.createElement('div');
            row.classList.add('row', 'seat-row');

            const rowLabel = document.createElement('div');
            rowLabel.classList.add('row-label');
            rowLabel.innerHTML = i;
            row.appendChild(rowLabel);

            seatContainer.appendChild(row);

            for (const j in rows[i]) {
                const seat = document.createElement('div');
                seat.dataset.seatId = rows[i][j]['id'];
                seat.dataset.seatNumber = rows[i][j]['seat_number'];
                seat.dataset.seatPrice = rows[i][j]['price'];
                seat.classList.add('seat');
                seat.id = `seat-${rows[i][j]['id']}`;

                if (rows[i][j]['is_booked']) {
                    seat.classList.add('sold');
                }
                if (rows[i][j]['is_locked']) {
                    seat.classList.add('locked');
                }

                seat.innerHTML = rows[i][j]['number'];
                row.appendChild(seat);
            }
        }

        seatContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('seat') &&
                !e.target.classList.contains('sold') &&
                !e.target.classList.contains('locked')
            ) {
                if (e.target.classList.contains('selected')) {
                    unlockSeat(e.target.dataset.seatId, showTime);
                } else {
                    lockSeat(e.target.dataset.seatId, showTime);
                }
            }
        });

        function lockSeat(seatId, showTime) {
            connSocket.send(JSON.stringify({
                'source': 'lock',
                'seat_id': seatId,
                'show_time': showTime
            }));
        }

        function unlockSeat(seatId, showTime) {
            connSocket.send(JSON.stringify({
                'source': 'unlock',
                'seat_id': seatId,
                'show_time': showTime
            }));
        }
    }

    function updateSeat(data) {
        const seat = document.getElementById(`seat-${data.seat_id}`);
        const user = document.getElementById('user-info').dataset.userid;
        if (data.is_locked) {
            if (data.locked_by != user) {
                console.log('locked by another user');
                seat.classList.add('locked');
            } else {
                seat.classList.add('selected');
                updateSelectedCount();
            }
        } else {
            seat.classList.remove('selected');
            seat.classList.remove('locked');
            updateSelectedCount();
        }
    }

    function updateSelectedCount() {
        const availableSeats = document.querySelectorAll(".seat-row .seat:not(.sold):not(.locked)");
        const count = document.getElementById('count');
        const total = document.getElementById('total');

        const selectedSeats = document.querySelectorAll('.seat-row .seat.selected');
        const seatsIndex = [...selectedSeats].map(seat => [...availableSeats].indexOf(seat));
        localStorage.setItem('selectedSeats', JSON.stringify(seatsIndex));

        const totalPrice = [...selectedSeats].reduce((total, seat) => {
            const seatPrice = parseFloat(seat.dataset.seatPrice);
            return total + seatPrice;
        }, 0);
        const selectedSeatsCount = selectedSeats.length;
        count.innerText = selectedSeatsCount;
        total.innerText = totalPrice;

        const checkoutButton = document.getElementById('checkout'); // Pay button
        if (selectedSeatsCount > 0) {
            checkoutButton.classList.remove('disabled');
        } else {
            checkoutButton.classList.add('disabled');
        }
    }

    // Add the checkout event listener inside the window.onload
    function handleCheckout() {
        const checkoutButton = document.getElementById('checkout');
        if (checkoutButton){
            checkoutButton.addEventListener('click', async () => {
                var paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
                const paymentOptionsContainer = document.getElementById('payment-options');

                paymentOptionsContainer.innerHTML = '';

                try{
                    const response = await fetch(`${base_url}/payment/payment-methods/`);
                    const paymentMethods = await response.json();

                    paymentMethods.forEach(method => {
                        const paymentOption = document.createElement('div');
                        paymentOption.classList.add('payment-option');
                        paymentOption.innerHTML = `
                            <img src="${method.logo}" alt="${method.name}"  class="payment-logo"/>
                        `;

                        paymentOption.addEventListener('click', () => {
                            const promoCode = document.getElementById('promoCode').value;
                            console.log(promoCode);
                            processPayment(method.name, movieSlug, theaterSlug, showTime, promoCode);
                        });

                        paymentOptionsContainer.appendChild(paymentOption);
                    });
                    paymentModal.show();

                } catch (error) {
                    console.log(error);
                }

            });

        }
    }
    handleCheckout();
});

async function processPayment(paymentMethod, movieSlug, theaterSlug, showTime, promoCode) {
    const total = document.getElementById('total').innerText;

    const chosenSeats = document.querySelectorAll('.seat.selected');
    const seatIds = [...chosenSeats]
        .map(seat => seat.dataset.seatId)
        .filter(seatId => seatId !== null && seatId !== undefined)
        .map(seatId => parseInt(seatId));
    
    const seatNumbers = [...chosenSeats]
        .map(seat => seat.dataset.seatNumber)
        .filter(seatNumber => seatNumber !== null && seatNumber !== undefined);

    const payload = {
        'payment_method': paymentMethod,
        'movie_slug': movieSlug,
        'theater_slug': theaterSlug,
        'show_time': showTime,
        'seat_ids': seatIds,
        'seat_numbers': seatNumbers,
        'promo_code': promoCode,
    }

    console.log(payload);
    try {
        const response = await fetch(`${base_url}/payment/process-payment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if(data.payment_url){
            window.open(data.payment_url, '_self');
        } else {
            console.log(data.error);
            alert('Payment failed');
        }
    } catch (error) {
        console.log(error);
    }

}
