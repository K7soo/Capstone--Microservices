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
    let referenceCounter = 1
    // Retrieve CSRF token
    const csrfToken = getCsrfToken();

    // Event listener for a button click
    const startCheckoutButton = document.getElementById("startCheckout");
    if (startCheckoutButton) {
        startCheckoutButton.addEventListener("click", () => {
            // Gather dynamic data from the form
            const maindescription = document.getElementById("checkoutDescription").value;
            const description = document.getElementById("itemDescription").value;
            const amount = parseInt(document.getElementById("itemAmount").value) * 100; // Convert to centavos
            const name = document.getElementById("itemName").value;
            const paymentMethod = document.getElementById("paymentMethod").value; // Get selected payment method
            const referenceNumber = `REF-${String(referenceCounter).padStart(3, '0')}`;
            referenceCounter++; // Increment for the next transaction
            success_url = "http://127.0.0.1:8001/success/"

            const payload = {
                data: {
                    attributes: {
                        send_email_receipt: true,
                        show_description: true,
                        show_line_items: true,
                        description: maindescription,   // place order
                        success_url: success_url,       // manage order URL
                        line_items: [
                            {
                                currency: "PHP",
                                amount: amount, // Amount in centavos
                                description: description, //sample description
                                name: name,               // Food item
                                quantity: 1
                            }
                        ],
                        payment_method_types: [paymentMethod],
                        reference_number: referenceNumber
                    }
                }
            };

            // Make the POST request
            fetch('/create-checkout-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // CSRF token for Django
                },
                body: JSON.stringify(payload), // Send the data payload
            })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then((error) => {
                        console.error("Error details:", error);
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then((data) => {
                console.log("Response:", data); // Log the response for debugging
                const checkout_url = data.details?.data?.attributes?.checkout_url;
                if (checkout_url) {
                    // Redirect to the PayMongo checkout page
                    window.location.href = checkout_url;
                } else {
                    console.error("Checkout URL not found in response.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        });
    } else {
        console.error("Start checkout button not found.");
    }
});
