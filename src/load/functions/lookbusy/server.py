from shutil import ExecError
from flask import Flask, request, jsonify
import os, traceback

# import user code
msg = None
try:
  from main import main
except:
  msg = traceback.format_exc()
  def main(args):
    return {"Code import error":msg}, 500

port = os.environ.get("__IL_PORT", 8080)
host = os.environ.get("__IL_HOST", "0.0.0.0")

app = Flask(__name__)
# app.config["SERVER_NAME"] = "{}:{}".format(host, port)
print(host, port)

@app.route('/')
def index():
  if msg is not None:
    return {"Status":"code import error", "code import error":msg}, 500
  else:
    return jsonify({"Status":"OK"})

@app.route('/invoke', methods=["POST"])
def invoke():
  # TODO: enforce concurrency limit
  # TODO: security to confirm invocation is from authorized source?
  try:
    json_input = request.get_json()
    ret = main(json_input)
    if type(ret) is tuple:
      return ret
    else:
      return jsonify(ret)
  except Exception as e:
    return jsonify({"Error":str(e)}), 500