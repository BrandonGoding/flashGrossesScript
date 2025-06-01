from datetime import datetime, time
from zoneinfo import ZoneInfo

from decouple import config
from square import Square
from square.environment import SquareEnvironment
from square.core.api_error import ApiError
import smtplib
from email.message import EmailMessage

TICKET_CATEGORY_ID = config("SQUARE_TICKET_CAT")


def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config("EMAIL_USERNAME")
    msg["To"] = to_email
    msg["Cc"] = config("CC_EMAIL")
    msg.set_content(body)

    with smtplib.SMTP(config("SMTP_SERVER"), config("SMTP_PORT")) as server:
        server.starttls()
        server.login(config("EMAIL_USERNAME"), config("EMAIL_PASSWORD"))
        server.send_message(msg)


def create_square_client():
    return Square(
        environment=SquareEnvironment.PRODUCTION, token=config("SQUARE_ACCESS_TOKEN")
    )


def get_time_range():
    eastern = ZoneInfo("America/New_York")
    now_et = datetime.now(eastern)
    start_et = datetime.combine(now_et.date(), time.min, tzinfo=eastern)
    end_et = datetime.combine(now_et.date(), time.max, tzinfo=eastern)
    return start_et.isoformat(), end_et.isoformat()


def fetch_payments(client, start_time, end_time, location_id):
    try:
        response = client.payments.list(
            begin_time=start_time, end_time=end_time, location_id=location_id
        )
        return [payment.order_id for payment in response.items]
    except ApiError as e:
        for error in e.errors:
            print(error.category)
            print(error.code)
            print(error.detail)
        return []


def fetch_orders(client, order_ids):
    orders = []
    for order_id in order_ids:
        try:
            response = client.orders.get(order_id=order_id)
            orders.append(response.order)
        except ApiError:
            pass
    return orders


def summarize_line_items(orders):
    summary = {}
    for order in orders:
        if order.line_items:
            for item in order.line_items:
                name = item.name
                quantity = int(item.quantity)
                revenue = int(item.total_money.amount)
                if name in summary:
                    summary[name]["quantity"] += quantity
                    summary[name]["revenue"] += revenue
                else:
                    summary[name] = {
                        "quantity": quantity,
                        "revenue": revenue,
                    }
    return summary


def get_ticket_item_names(client):
    ticket_names = []
    full_catalog = client.catalog.list(types="ITEM")
    for item in full_catalog.items:
        if item.item_data.categories:
            for category in item.item_data.categories:
                if category.id == TICKET_CATEGORY_ID:
                    ticket_names.append(item.item_data.name)
    return ticket_names


def filter_ticket_items(line_items, ticket_item_names):
    for item in list(line_items.keys()):
        if item not in ticket_item_names:
            del line_items[item]
    return line_items


def email_owner_info(line_items):
    lines = ["Item Sales Summary:\n"]
    for name, data in line_items.items():
        lines.append(f"{name}: {data['quantity']} sold for ${data['revenue']/100:.2f}")
    body = "\n".join(lines)
    send_email("Daily Sales Summary", body, config("OWNER_EMAIL"))


def master_ticket_report(ticket_summary):
    lines = ["🎟 Ticket Sales Summary:\n"]
    for name, data in ticket_summary.items():
        lines.append(
            f"{name}: {data['quantity']} sold, ${data['revenue']/100:.2f} revenue"
        )

    # Append today's date in Eastern Time
    today_et = datetime.now(ZoneInfo("America/New_York")).strftime("%B %-d, %Y")
    lines.append(f"\nReport generated for {today_et}")

    body = "\n".join(lines)
    send_email(config("TICKET_REPORT_SUBJECT"), body, config("REPORT_EMAIL"))


def main():
    location_id = config("SQUARE_LOCATION_ID")
    client = create_square_client()
    start_time, end_time = get_time_range()

    order_ids = fetch_payments(client, start_time, end_time, location_id)
    orders = fetch_orders(client, order_ids)
    line_items = summarize_line_items(orders)
    email_owner_info(line_items)
    ticket_item_names = get_ticket_item_names(client)
    ticket_summary = filter_ticket_items(line_items, ticket_item_names)
    master_ticket_report(ticket_summary)


if __name__ == "__main__":
    main()
