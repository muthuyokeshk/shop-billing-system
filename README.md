# Shop Billing System

A command-line Shop Billing System developed using Python and SQLite.

This project was developed as part of the Python Fresher Assessment for:

**Tekistic IT Services Pvt Ltd**

The system allows users to manage products and stock, create customer bills, calculate GST, and view previously generated bills.

## Features

- Add new products with product code, name, price, stock, and GST rate
- List all available products
- Create customer bills
- Calculate taxable value, CGST, SGST, round-off, and grand total
- Validate product codes, prices, quantities, and stock availability
- Combine duplicate products in the same bill
- Automatically reduce stock after a successful bill
- Update product stock
- View past bills
- Store product, bill, and bill-item data using SQLite
- Generate sequential bill numbers starting from 1001
- Use parameterized SQL queries for database operations

## Technologies Used

- Python 3.10+
- SQLite
- Python `sqlite3` module
- Python standard library
- Command Line Interface (CLI)

## How to Run

1. Make sure Python 3.10 or later is installed.
2. Open a terminal or command prompt in the project folder.
3. Run the program using:

```bash
python shop_billing.py
```

The program uses SQLite and automatically creates `shop.db` in the project folder.

## Completed Assessment Levels

### Level 1
- Product management
- Product listing
- Customer billing
- Input validation
- Sequential bill numbering

### Level 2
- SQLite database integration
- Stock management
- GST calculation
- CGST and SGST calculation
- Round-off calculation
- Duplicate product handling in a bill
- Past bill viewing
- Transaction rollback for failed bill saving

### Level 3
Not implemented. Level 3 features are optional.

## Database Design

The application uses SQLite with three tables:

### `products`

Stores product information.

- `product_code` — Unique product code
- `name` — Product name
- `price` — Unit price
- `stock` — Available stock quantity
- `gst_rate` — GST percentage

### `bills`

Stores bill information.

- `bill_number` — Unique bill number
- `bill_date` — Date of the bill
- `customer_name` — Customer name

### `bill_items`

Stores the products included in each bill.

- `bill_number` — Bill reference
- `product_code` — Product reference
- `quantity` — Quantity purchased
- `rate` — Product rate
- `amount` — Line-item amount

## Assumptions

- GST rates are limited to 0%, 5%, 12%, and 18%.
- Product codes must be unique.
- Price and stock quantities must be positive.
- Billing quantity must be a positive whole number.
- A bill cannot be created without at least one valid product.
- A bill cannot be created when the requested quantity exceeds available stock.
- If the same product is entered multiple times in one bill, the quantities are combined.
- Bill numbers start from 1001 and continue sequentially.
- GST is divided equally between CGST and SGST.
- The SQLite database file `shop.db` is created in the project folder.

## Possible Improvements

- Add daily sales summary
- Add low-stock and reorder alerts
- Export bills to CSV or PDF
- Add automated unit tests
- Add Indian currency amount in words

## Author

**Muthu Yokesh K.**

Python Fresher Assessment  
Tekistic IT Services Pvt Ltd