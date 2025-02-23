from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper  # Ensure this is correct
import generic_helper

app = FastAPI()

inprogress_orders={}
@app.post("/")
async def handle_request(request: Request):
    # Retrieve JSON data from request
    payload = await request.json()

    # Extract intent and parameters
    intent = payload.get('queryResult', {}).get('intent', {}).get('displayName', '')
    parameters = payload.get('queryResult', {}).get('parameters', {})
    output_contexts=payload.get('queryResult',{}).get('outputContexts',{})

    # Debugging log 
    print(f"Received Intent: {intent}")
    print(f"Received Parameters: {parameters}")

    # Extract session ID safely
    session_id = None
    if output_contexts:
        session_id = generic_helper.extract_session_id(output_contexts[0]['name'])
    intent_handler_dict={
        'order.add-context:ongoing-order':add_to_order,
        'order.remove-context: ongoing-order':remove_from_order,
        'Order.complete-context ongoing-order':complete_order,
        'track.order-context ongoing-tracking':track_order
    }
    # Check if intent exists in handler dictionary
    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters,session_id)

def save_to_db(order:dict):
    next_order_id = db_helper.get_or_create_order_id()

    # Insert individual items along with quantity in orders table
    for movie_name, tickets in order.items():
        rcode = db_helper.insert_order_item(
            movie_name,
            tickets,
            next_order_id
        )

        if rcode == -1:
            return -1

    # Now insert order tracking status
    db_helper.insert_order_tracking(next_order_id, "in progress")

    return next_order_id



def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)

            fulfillment_text = f"Thank you for booking your ticket with Moonlight Movies! 🌙✨ " \
                           f"Here is your order id # {order_id}. " \
                           f"Your order total is {order_total} "\
                            f"Your ticket is confirmed! Please arrive 15 minutes before the showtime for a smooth experience. Enjoy your movie! 🍿🎥 "\
                            f"Need help regarding seat number? Reply here CHECK SEAT NO"\
                            f"Happy Watching! 😊"


                           
            del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def add_to_order(parameters: dict,session_id:str):
    movie_name = parameters.get("Movie-name", []) 
    tickets = parameters.get("number", [])

    # Ensure both values are lists
    if not isinstance(movie_name, list):
        movie_name = [movie_name]
    if not isinstance(tickets, list):
        tickets = [tickets]

    if len(movie_name) != len(tickets):
        fulfillment_text = "Sorry, I didn't understand. Please specify the movie name and the number of tickets clearly!"
    else:
        new_movie_dict=dict(zip(movie_name,tickets))
        if session_id in inprogress_orders:
            current_movie_dict=inprogress_orders[session_id]
            current_movie_dict.update(new_movie_dict)
            inprogress_orders[session_id]=current_movie_dict

        else:
            inprogress_orders[session_id]=new_movie_dict
        
        order_str=generic_helper.get_str_from_movie_dict(inprogress_orders[session_id])

 
        fulfillment_text = f"so far of your booking {order_str}. Shall we move on with it?"


    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    movie_name = parameters["movie-name"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in movie_name:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_movie_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



def track_order(parameters: dict,session_id:str):
    # Check if "number" key exists in parameters (Dialogflow sends number, not order_id)
    if "number" not in parameters:
        return JSONResponse(content={"fulfillmentText": "Order ID is missing. Please provide a valid Order ID."})

    try:
        order_id = int(parameters["number"])  # Use "number" instead of "order_id"
    except ValueError:
        return JSONResponse(content={"fulfillmentText": "Invalid Order ID. Please enter a numeric value."})

    # Fetch order details
    order_details = db_helper.get_order_details(order_id)

    if not order_details:
        return JSONResponse(content={"fulfillmentText": "No order found for this order ID."})

    response=[]

    for order in order_details:
        response.append(f"Your booking details:\n"
            f"🎬 Movie: {order['movie_name']}\n"
            f"🎟️ Seat Number: {order['seat_numbers']}\n"
            f"⏰ Time Slot: {order['time_slot']}")
    return JSONResponse(content={"fulfillmentText": "\n".join(response)})



    
