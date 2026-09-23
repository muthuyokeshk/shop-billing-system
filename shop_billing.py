# Shop Billing System
# Tekistic IT Services Pvt Ltd - Python Fresher Assessment


import sqlite3
from datetime import date

# Connect to the SQLite database
connection = sqlite3.connect("shop.db")

print("Database connected successfully!")


#Product Table:
connection.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    gst_rate REAL NOT NULL
)
""")

connection.commit()

print("Products table created successfully!")


#Bills Table:
connection.execute("""
CREATE TABLE IF NOT EXISTS bills (
    bill_number INTEGER PRIMARY KEY,
    bill_date TEXT NOT NULL,
    customer_name TEXT NOT NULL
)
""")

connection.commit()

print("Bills table created successfully!")


#Bill_item Table:
connection.execute("""
CREATE TABLE IF NOT EXISTS bill_items (
    bill_number INTEGER,
    product_code TEXT,
    quantity INTEGER,
    rate REAL,
    amount REAL,
    FOREIGN KEY (bill_number) REFERENCES bills(bill_number),
    FOREIGN KEY (product_code) REFERENCES products(product_code)
)
""")

connection.commit()

print("Bill items table created successfully!")


products = [
    ("P101", "Basmati Rice 1 kg", 120.00, 50, 5),
    ("P102", "Sunflower Oil 1L", 180.00, 30, 5),
    ("P103", "Toothpaste 150g", 95.00, 40, 18),
    ("P104", "Notebook A4", 60.00, 100, 12),
    ("P105", "Milk 500ml", 28.00, 20, 0)
]

connection.executemany("""
INSERT OR IGNORE INTO products
(product_code, name, price, stock, gst_rate)
VALUES (?, ?, ?, ?, ?)
""", products)

connection.commit()

print("Sample products inserted successfully!")


# Add a new product
def add_product():

    product_code = input("Enter product code: ")
    name = input("Enter product name: ")

    # Validate price
    while True:
        try:
            price = float(input("Enter price: "))

            if price > 0:
                break
            else:
                print("Price must be positive.")

        except ValueError:
            print("Invalid price. Please enter a number.")

    # Validate stock
    while True:
        try:
            stock = int(input("Enter stock quantity: "))

            if stock > 0:
                break
            else:
                print("Stock must be positive.")

        except ValueError:
            print("Invalid stock. Please enter a whole number.")

    # Validate GST
    while True:
        try:
            gst_rate = float(input("Enter GST rate: "))

            if gst_rate in [0, 5, 12, 18]:
                break
            else:
                print("Invalid GST rate. Choose 0, 5, 12, or 18.")

        except ValueError:
            print("Invalid GST rate. Please enter a number.")

    # Insert product into database
    try:
        connection.execute("""
        INSERT INTO products (product_code, name, price, stock, gst_rate)
        VALUES (?, ?, ?, ?, ?)
        """, (product_code, name, price, stock, gst_rate))

        connection.commit()

        print("Product added successfully!")

    except sqlite3.IntegrityError:
        print("Product code already exists. Please use a different code.")


# List all products
def list_products():

    cursor = connection.execute("""
    SELECT * FROM products
    """)

    rows = cursor.fetchall()

    print(f"{'Code':<8}{'Name':<22}{'Price':>10}{'Stock':>8}{'GST':>8}")
    print("-" * 56)

    for row in rows:
        product_code, name, price, stock, gst_rate = row

        print(
            f"{product_code:<8}"
            f"{name:<22}"
            f"{price:>10.2f}"
            f"{stock:>8}"
            f"{gst_rate:>7.0f}%"
        )


# Get the next bill number
next_bill_number = connection.execute("""
SELECT COALESCE(MAX(bill_number), 1000) + 1
FROM bills
""").fetchone()[0]

print("Next bill number:", next_bill_number)


# Create a new bill
def create_bill():

    global next_bill_number

    bill_date = date.today().strftime("%d-%m-%Y")

    bill_items = []

    customer_name = input("Enter customer name: ")

    list_products()

    while True:
        product_code = input("Enter product code (or 'done' to finish): ")

        if product_code.lower() == "done":
            break

        cursor = connection.execute("""
        SELECT * FROM products
        WHERE product_code = ?
        """, (product_code,))

        product = cursor.fetchone()

        if product is None:
            print("Product code not found.")
            continue

        while True:
            try:
                quantity = int(input("Enter quantity: "))

                if quantity > 0:
                    break
                else:
                    print("Quantity must be positive.")

            except ValueError:
                print("Invalid quantity. Please enter a whole number.")

        if quantity > product[3]:
            print("Insufficient stock.")
            continue

        existing_item = None

        for item in bill_items:
            if item[0] == product[0]:
                existing_item = item
                break

        if existing_item is not None:

            new_quantity = existing_item[3] + quantity

            if new_quantity > product[3]:
                print("Insufficient stock for combined quantity.")
                continue

            new_amount = product[2] * new_quantity

            bill_items.remove(existing_item)

            bill_items.append(
                (
                    product[0],
                    product[1],
                    product[2],
                    new_quantity,
                    new_amount,
                    product[4]
                )
            )

            print("Updated quantity:", new_quantity)
            print("Amount:", new_amount)

        else:

            amount = product[2] * quantity

            bill_items.append(
                (
                    product[0],
                    product[1],
                    product[2],
                    quantity,
                    amount,
                    product[4]
                )
            )

            print("Amount:", amount)

    if len(bill_items) == 0:
        print("No products added. Bill was not created.")
        return

    try:

        connection.execute("""
        INSERT INTO bills (bill_number, bill_date, customer_name)
        VALUES (?, ?, ?)
        """, (next_bill_number, bill_date, customer_name))

        for item in bill_items:

            product_code, name, price, quantity, amount, gst_rate = item

            connection.execute("""
            INSERT INTO bill_items
            (bill_number, product_code, quantity, rate, amount)
            VALUES (?, ?, ?, ?, ?)
            """, (next_bill_number, product_code, quantity, price, amount))

        for item in bill_items:

            product_code, name, price, quantity, amount, gst_rate = item

            connection.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE product_code = ?
            """, (quantity, product_code))

        connection.commit()

    except Exception as error:

        connection.rollback()

        print("Bill could not be saved.")
        print("Error:", error)

        return

    taxable_value = 0

    for item in bill_items:
        taxable_value = taxable_value + item[4]

    total_gst = 0

    for item in bill_items:

        amount = item[4]
        gst_rate = item[5]

        gst_amount = amount * gst_rate / 100

        total_gst = total_gst + gst_amount

    cgst = total_gst / 2
    sgst = total_gst / 2

    grand_total = taxable_value + total_gst

    rounded_total = round(grand_total)

    round_off = rounded_total - grand_total

    print("\n========== BILL ==========")
    print("Bill No:", next_bill_number)
    print("Date:", bill_date)
    print("Customer:", customer_name)
    print("--------------------------")

    print(
        f"{'Product':<22}"
        f"{'Qty':>5}"
        f"{'Rate':>10}"
        f"{'Amount':>12}"
        f"{'GST':>7}"
    )

    print("-" * 56)

    for item in bill_items:

        product_code, name, price, quantity, amount, gst_rate = item

        print(
            f"{name:<22}"
            f"{quantity:>5}"
            f"{price:>10.2f}"
            f"{amount:>12.2f}"
            f"{gst_rate:>6.0f}%"
        )

    print("-" * 56)

    print(f"{'Taxable Value:':>44}{taxable_value:>12.2f}")
    print(f"{'CGST:':>44}{cgst:>12.2f}")
    print(f"{'SGST:':>44}{sgst:>12.2f}")
    print(f"{'Round-off:':>44}{round_off:>12.2f}")
    print(f"{'Grand Total:':>44}{rounded_total:>12}")

    print("\nStock after saving:")

    for item in bill_items:

        product_code = item[0]

        cursor = connection.execute("""
        SELECT stock
        FROM products
        WHERE product_code = ?
        """, (product_code,))

        current_stock = cursor.fetchone()[0]

        print(product_code, ":", current_stock)

    next_bill_number = next_bill_number + 1


# Update stock
def update_stock():

    product_code = input("Enter product code: ")

    cursor = connection.execute("""
    SELECT * FROM products
    WHERE product_code = ?
    """, (product_code,))

    product = cursor.fetchone()

    if product is None:
        print("Product code not found.")
        return

    print("Product:", product[1])
    print("Current stock:", product[3])

    while True:
        try:
            quantity = int(input("Enter stock to add: "))

            if quantity > 0:
                break
            else:
                print("Stock quantity must be positive.")

        except ValueError:
            print("Invalid quantity. Please enter a whole number.")

    connection.execute("""
    UPDATE products
    SET stock = stock + ?
    WHERE product_code = ?
    """, (quantity, product_code))

    connection.commit()

    print("Stock updated successfully!")


# View past bill
def view_bill():

    try:
        bill_number = int(input("Enter bill number: "))
    except ValueError:
        print("Invalid bill number.")
        return

    cursor = connection.execute("""
    SELECT bill_number, bill_date, customer_name
    FROM bills
    WHERE bill_number = ?
    """, (bill_number,))

    bill = cursor.fetchone()

    if bill is None:
        print("Bill not found.")
        return

    print("\n========== PAST BILL ==========")
    print("Bill No:", bill[0])
    print("Date:", bill[1])
    print("Customer:", bill[2])
    print("-------------------------------")

    cursor = connection.execute("""
    SELECT bill_items.product_code,
           products.name,
           bill_items.quantity,
           bill_items.rate,
           bill_items.amount,
           products.gst_rate
    FROM bill_items
    JOIN products
    ON bill_items.product_code = products.product_code
    WHERE bill_items.bill_number = ?
    """, (bill_number,))

    items = cursor.fetchall()

    if not items:
        print("No bill items found.")
        return

    print(
        f"{'Product':<22}"
        f"{'Qty':>5}"
        f"{'Rate':>10}"
        f"{'Amount':>12}"
        f"{'GST':>7}"
    )

    print("-" * 56)

    taxable_value = 0
    total_gst = 0

    for item in items:

        product_code, name, quantity, rate, amount, gst_rate = item

        print(
            f"{name:<22}"
            f"{quantity:>5}"
            f"{rate:>10.2f}"
            f"{amount:>12.2f}"
            f"{gst_rate:>6.0f}%"
        )

        taxable_value = taxable_value + amount

        gst_amount = amount * gst_rate / 100
        total_gst = total_gst + gst_amount

    cgst = total_gst / 2
    sgst = total_gst / 2

    grand_total = taxable_value + total_gst

    rounded_total = round(grand_total)

    round_off = rounded_total - grand_total

    print("-" * 56)

    print(f"{'Taxable Value:':>44}{taxable_value:>12.2f}")
    print(f"{'CGST:':>44}{cgst:>12.2f}")
    print(f"{'SGST:':>44}{sgst:>12.2f}")
    print(f"{'Round-off:':>44}{round_off:>12.2f}")
    print(f"{'Grand Total:':>44}{rounded_total:>12}")


# Main menu
while True:

    print("\n========== SHOP BILLING SYSTEM ==========")
    print("1. Add Product")
    print("2. List Products")
    print("3. Create Bill")
    print("4. Update Stock")
    print("5. View Past Bill")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_product()

    elif choice == "2":
        list_products()

    elif choice == "3":
        create_bill()

    elif choice == "4":
        update_stock()

    elif choice == "5":
        view_bill()

    elif choice == "6":
        print("Thank you. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")

