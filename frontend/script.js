const API_URL = "http://127.0.0.1:8001";

// Load products
async function loadProducts() {
    try {
        const response = await fetch(API_URL + "/products");

        if (!response.ok) {
            throw new Error("Failed to load products");
        }

        const products = await response.json();

        const container = document.getElementById("products");
        container.innerHTML = "";

        products.forEach(function(product) {
            container.innerHTML += `
                <div>
                    <h3>${product.name}</h3>
                    <p>Category: ${product.category}</p>
                    <p>Price: ₹${product.price}</p>
                    <p>Stock: ${product.stock}</p>
                </div>
                <hr>
            `;
        });

    } catch (error) {
        console.log(error);
        alert("Failed to load products");
    }
}


// Add product
document.getElementById("productForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const product = {
        name: document.getElementById("name").value,
        category: document.getElementById("category").value,
        price: Number(document.getElementById("price").value),
        stock: Number(document.getElementById("quantity").value)
    };

    try {

        const response = await fetch(API_URL + "/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(product)
        });

        if (response.ok) {

            alert("Product added successfully!");

            document.getElementById("productForm").reset();

            loadProducts();

        } else {

            alert("Failed to add product");

            console.log(await response.text());
        }

    } catch (error) {

        console.log(error);
        alert("Connection error");

    }

});

// Load customers
async function loadCustomers() {
    try {
        const response = await fetch(API_URL + "/customers");

        if (!response.ok) {
            throw new Error("Failed to load customers");
        }

        const customers = await response.json();

        const container = document.getElementById("customers");
        container.innerHTML = "";

        customers.forEach(function(customer) {
            container.innerHTML += `
                <div>
                    <h3>${customer.name}</h3>
                    <p>Phone: ${customer.phone}</p>
                    <p>Email: ${customer.email || "N/A"}</p>
                    <p>Address: ${customer.address || "N/A"}</p>
                </div>
                <hr>
            `;
        });

    } catch (error) {
        console.log(error);
        alert("Failed to load customers");
    }
}

// Load sales
async function loadSales() {
    try {
        const response = await fetch(API_URL + "/sales");

        if (!response.ok) {
            throw new Error("Failed to load sales");
        }

        const sales = await response.json();

        const container = document.getElementById("sales");
        container.innerHTML = "";

        sales.forEach(function(sale) {
            container.innerHTML += `
                <div>
                    <h3>Sale ID: ${sale.id}</h3>
                    <p>Total Amount: ₹${sale.total_amount}</p>
                </div>
                <hr>
            `;
        });

    } catch (error) {
        console.log(error);
        alert("Failed to load sales");
    }
}

// Load feedback
async function loadFeedback() {
    try {
        const response = await fetch(API_URL + "/feedback");

        if (!response.ok) {
            throw new Error("Failed to load feedback");
        }

        const feedback = await response.json();

        const container = document.getElementById("feedback");
        container.innerHTML = "";

        feedback.forEach(function(item) {
            container.innerHTML += `
                <div>
                    <h3>Rating: ${item.rating}/5</h3>
                    <p>Customer ID: ${item.customer_id}</p>
                    <p>${item.message}</p>
                </div>
                <hr>
            `;
        });

    } catch (error) {
        console.log(error);
        alert("Failed to load feedback");
    }
}

// Load bill
async function loadBill() {
    const saleId = document.getElementById("billSaleId").value;

    if (!saleId) {
        alert("Enter Sale ID");
        return;
    }

    try {
        const response = await fetch(
            API_URL + "/sales/" + saleId + "/bill"
        );

        if (!response.ok) {
            throw new Error("Failed to load bill");
        }

        const bill = await response.json();

        const container = document.getElementById("bill");

        container.innerHTML = `
            <h3>Sale ID: ${saleId}</h3>
            <p>Total Amount: ₹${bill.total_amount}</p>
        `;

    } catch (error) {
        console.log(error);
        alert("Failed to load bill");
    }
}