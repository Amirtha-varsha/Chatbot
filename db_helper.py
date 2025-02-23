import mysql.connector

# Establish database connection
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mkvarsha#03",
    database="moviebookingsdb"
)

# Function to get the current session's order_id or create a new one
def get_or_create_order_id():
    cursor = cnx.cursor()

    # Check if there's an existing order for this session
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1
# Function to call the MySQL stored procedure and insert an order item

def insert_order_item(movie_name, tickets, order_id):
    try:
       cursor = cnx.cursor()
       tickets = int(float(tickets))
       # Fetch movie_id (needed for seat allocation)
       cursor.execute("SELECT movie_id FROM movies WHERE movie_name = %s", (movie_name,))
       movie_id_result = cursor.fetchone()
       if not movie_id_result:
        print(f"Error: Movie '{movie_name}' not found.")
        return -1
       movie_id = movie_id_result[0]
       # Fetch the next available seat number
       seat_number = get_next_seat_number(movie_id,tickets)
       if not seat_number:
        print("Error: No available seats.")
        return -1
       
       cursor.callproc('insert_new_order', (order_id, movie_name, tickets, seat_number))
    
       cnx.commit()
       cursor.close()
       print("Order item inserted successfully!")
       return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

def get_total_order_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()
    if result is None:
        return 0  # Return 0 if no order is found

    return result[0]

    # Closing the cursor
    cursor.close()

    return result

import string

# Function to get the next available seat number
def get_next_seat_number(movie_id,tickets):
    tickets = int(float(tickets))
    cursor = cnx.cursor()

    # Query to get the last assigned seat for the given movie
    query = "SELECT seat_number FROM orders WHERE movie_id = %s ORDER BY LENGTH(seat_number), seat_number"
    cursor.execute(query, (movie_id,))

    result = cursor.fetchall()

    # Close the cursor
    cursor.close()

    # Define seat configuration
    rows = list(string.ascii_uppercase[:10])  # Rows A-J (modify as needed)
    seats_per_row = 10  # Number of seats in each row

    assigned_seats = set()
    if result:
        for row in result:
            assigned_seats.update(row[0].split(','))  # Split multiple seats
    available_seats=[]

    for row in rows:
        for num in range(1, seats_per_row + 1):
            seat = f"{row}{num}"
            if seat not in assigned_seats:
                available_seats.append(seat)
                if len(available_seats) == tickets:
                    return ", ".join(available_seats)  # Return only required seats
    return None


# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()
    # Closing the cursor
    cursor.close()



# Function to fetch order details (movie name, seat number, time slot)
def get_order_details(order_id):
    cursor = cnx.cursor()

    # SQL query to fetch movie name, seat number, and time slot
    query = """SELECT m.movie_name, o.seat_number, m.time_slot
               FROM orders o
               JOIN movies m ON o.movie_id = m.movie_id
               WHERE o.order_id = %s"""
    
    cursor.execute(query, (order_id,))
    result = cursor.fetchall()  # Fetch one record

    # If no records found
    if not result:
        return None
    

    # Prepare a structured response for all movies in the order
    order_details = []
    for row in result:
        movie_name = row[0]
        time_slot = row[2]
        seat_numbers = ", ".join(sorted(row[1].split(',')))  # Sorting for consistency
        order_details.append({
            "movie_name": movie_name,
            "seat_numbers": seat_numbers,
            "time_slot": time_slot
        })

    return order_details