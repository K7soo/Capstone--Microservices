document.addEventListener("DOMContentLoaded", () => {
    // Function to extract CSRF token from cookies
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmedCookie = cookie.trim();
            if (trimmedCookie.startsWith('csrftoken=')) {
                return trimmedCookie.split('=')[1];
            }
        }
        console.error("CSRF token not found in cookies.");
        return null; // Return null if no CSRF token is found
    }

    // Retrieve CSRF token
    const csrfToken = getCsrfToken();

    // Data payload for the fetch request
    const data = {
        data: {
            attributes: {
                send_email_receipt: true,
                show_description: true,
                show_line_items: true,
                description: 'Description',
                line_items: [
                    {
                        currency: 'PHP',
                        amount: 2000, // Amount in centavos
                        description: 'testing',
                        name: 'Product',
                        quantity: 1
                    }
                ],
                payment_method_types: [
                    'gcash',
                    'grab_pay',
                    'card',
                    'qrph',
                    'brankas_bdo',
                    'brankas_landbank',
                    'paymaya'
                ],
                reference_number: '001'
            }
        }  
    };

    // Event listener for the button click
    const startCheckoutButton = document.getElementById("startCheckout");
    if (startCheckoutButton) {
        startCheckoutButton.addEventListener("click", () => {
            console.log('Sending payload:', JSON.stringify(data, null, 2));
            fetch('https://api.paymongo.com/v1/checkout_sessions', {
                method: 'POST',
                headers: {
                    accept: 'application/json',
                    'Content-Type': 'application/json',
                    authorization: 'Basic c2tfdGVzdF9MZlpSbnR5eG1aSmFoN2lhRmJZa2tmVGM6'
                },
                body: JSON.stringify(data), // Send the data payload
            })
            .then((res) => {
                if (!res.ok) {
                    return res.json().then((errorDetails) => {
                        console.error('Error details:', errorDetails);
                        throw new Error(`HTTP error! Status: ${res.status}`);
                    });
                }
                return res.json();
            })
            .then((res) => {
                console.log('Response:', res); // Log the response for debugging
                if (res.data?.attributes?.checkout_url) {
                    // Redirect to the PayMongo checkout page
                    window.location.href = res.data.attributes.checkout_url;
                    console.log(res)
                } else {
                    console.error('Checkout URL not found in response.');
                }
            })
            .catch((err) => {
                console.error('Error:', err);
            });
        });
    } else {
        console.error("Start checkout button not found.");
    }
});
