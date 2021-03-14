from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import pymysql
import json

app = Flask(__name__)
app.secret_key = "shhhhhh"


db = pymysql.connect(host="localhost", user="root",
                     password="admin123", database="marathon")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/inventory")
def inventory():
    cur = db.cursor()

    cur.execute("SELECT * FROM inventory")
    inventory = cur.fetchall()

    return render_template("inventory.html", inventory=inventory)


@app.route("/addproduct/", methods=["POST", "GET"])
def addproduct():
    cur = db.cursor()

    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]

        cur.execute(
            "INSERT INTO inventory (name, quantity) VALUES (%s, %s)", (name, quantity))

        db.commit()

        flash("Added to inventory", "success")

        return redirect(url_for("inventory"))

    return render_template("addproduct.html")


@app.route("/product/<id>", methods=["POST", "GET"])
def product(id):
    cur = db.cursor()

    cur.execute("SELECT * FROM inventory WHERE id = %s", id)
    product = cur.fetchone()

    if request.method == "POST":
        quantity = request.form['quantity']

        cur.execute(
            "INSERT INTO cart (name, quantity) VALUES (%s, %s)", (product[1], quantity))

        db.commit()

        flash("Added to cart", "success")

        return redirect(url_for("cart"))

    return render_template("product.html", product=product)


@app.route("/cart", methods=["POST", "GET"])
def cart():
    cur = db.cursor()

    cur.execute("SELECT * FROM cart")
    cart = cur.fetchall()

    results = None

    if request.method == "POST":
        search = request.form.get("search")
        parameter = request.form.get("parameter")

        cur.execute("SELECT id, name FROM inventory WHERE {} LIKE '%{}%'".format(
            parameter, search))

        results = cur.fetchall()

    return render_template("cart.html", cart=cart, results=results)


@app.route("/removecart/<id>")
def removecart(id):
    cur = db.cursor()

    cur.execute("DELETE FROM cart WHERE id = %s", id)

    db.commit()

    flash("Item removed", "danger")

    return redirect(url_for("cart"))


@app.route("/sendcart")
def sendcart():
    cur = db.cursor()

    cur.execute("SELECT * FROM cart")

    cart = cur.fetchall()

    if not cart:
        flash("You can't send an empty cart", "danger")
        return redirect(url_for("cart"))

    cart = [{'id': x[0], 'name': x[1], 'quantity': x[2]} for x in cart]

    jsoncart = json.dumps(cart)

    for x in cart:
        cur.execute("UPDATE inventory SET quantity = quantity + %s WHERE name = %s",
                    (x['quantity'], x['name']))

    cur.execute("SELECT MAX(cart_id) FROM cart_history")

    cartid = cur.fetchone()[0]

    if not cartid:
        cartid = 0

    for x in cart:
        cur.execute("INSERT INTO cart_history(cart_id, name, quantity) VALUES (%s, %s, %s)",
                    (cartid+1, x['name'], x['quantity']))

    cur.execute("TRUNCATE TABLE cart")

    db.commit()

    send = requests.post("http://127.0.0.1:8008/", data=jsoncart)

    flash("<Response [{}]> ".format(
        send.status_code)+str(send.json()), "success")

    return redirect(url_for("inventory"))


@app.route("/history")
def history():
    cur = db.cursor()

    history = []

    id = 1

    cont = True

    while cont == True:
        cur.execute("SELECT * FROM cart_history WHERE cart_id = %s", id)

        x = cur.fetchall()
        if x:
            history.append(x)
            id += 1
        else:
            cont = False

    return render_template("history.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
