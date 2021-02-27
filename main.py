from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    items = db.relationship('Item', backref='list', lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)


db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        list_title = request.form["list"]
        list_id = List.query.filter_by(title=list_title).first()
        new_todo = Item(
            title=request.form["newItem"],
            list_id=list_id.id
        )
        db.session.add(new_todo)
        db.session.commit()
        if list_title != "Welcome!":
            return redirect(f"/{list_title}")
    todo_items = Item.query.filter_by(list_id=1).all()
    return render_template("list.html", todos=todo_items, list_title="Welcome!")


@app.route("/<list_name>", methods=["GET", "POST"])
def custom_list(list_name):
    if List.query.filter_by(title=list_name).first() is not None:
        list_id = List.query.filter_by(title=list_name).first()
        todo_items = Item.query.filter_by(list_id=list_id.id).all()
        return render_template("list.html", todos=todo_items, list_title=list_name)
    else:
        new_list = List(
            title=list_name
        )
        db.session.add(new_list)
        db.session.commit()
        list_id = List.query.filter_by(title=list_name).first()
        todo_items = Item.query.filter_by(list_id=list_id.id).all()
        return render_template("list.html", todos=todo_items, list_title=list_name)


@app.route("/delete", methods=["POST"])
def delete():
    todo_id = request.form["checkbox"]
    todo_item = Item.query.filter_by(id=todo_id).first()
    db.session.delete(todo_item)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
