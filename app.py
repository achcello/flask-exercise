from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


@app.route("/users", methods=["GET", "POST"])
def get_users():
    if request.method == "GET":
        team = request.args.get("team")
        if team is not None:
            data = {"users": db.getByTeam("users", team)}
            return create_response(data)
        data = {"users": db.get("users")}
        print(data)
        return create_response(data)
    if request.method == "POST":
        data = request.form
        if "name" not in data or "age" not in data or "team" not in data:
            status = 422
            message = (
                "The required information (name, age, and team) was" + " not given."
            )
            return create_response(status=status, message=message)
        status = 201
        data = db.create("users", dict(data))
        return create_response(data, status=status)


@app.route("/users/<id>", methods=["GET", "PUT", "DELETE"])
def get_by_id(id):
    id = int(id)
    if db.getById("users", id) is None:
        status = 404
        message = "A user could not be found for the given id."
        return create_response(status=status, message=message)
    if request.method == "GET":
        data = {"user": db.getById("users", id)}
        return create_response(data)
    if request.method == "PUT":
        status = 201
        data = dict(request.form)
        if "name" in data:
            data["name"] = data["name"][0]
        if "age" in data:
            data["age"] = int(data["age"][0])
        if "team" in data:
            data["team"] = data["team"][0]
        new = db.updateById("users", id, data)
        return create_response(new, status)
    if request.method == "DELETE":
        db.deleteById("users", id)
        message = "User " + str(id) + " has been deleted."
        return create_response(message=message)


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
