from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))


######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200


######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return jsonify({"message": "Internal server error"}), 500


######################################################################
# GET ALL PICTURES
######################################################################


@app.route("/picture", methods=["GET"])
def get_pictures():
    try:
        if not isinstance(data, list):
            raise TypeError('Data is not in list format!')
        return jsonify([
                picture['pic_url'] for picture in data
                if 'pic_url' in picture
            ]), 200
    except Exception as e:
        return jsonify({'Message': f'Error: {str(e)}'}), 500


######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    try:
        for picture in data:
            if int(picture['id']) == id:
                return jsonify(picture), 200

        # No matching picture was found with given ID
        return jsonify({
            'Message': f'No matching image found with ID of {str(id)}.'
        }), 404
    
    except Exception as e: 
        return jsonify({
            'Message': f'Internal error: {str(e)}. Data not found'
        }), 500


######################################################################
# CREATE A PICTURE
######################################################################


@app.route("/picture", methods=["POST"])
def create_picture():
    try:
        picture = request.get_json()

        # If the POSTed picture isn't formatted properly
        if not picture or 'id' not in picture:
            return jsonify({
                'Message': 'Missing or malformed picture data'
            }), 400

        # If an existing ID matches the POSTed ID for any picture
        if any(int(pic['id']) == int(picture['id']) for pic in data):
            return jsonify({
                'Message': f'picture with id {picture["id"]} already present'
            }), 302
            
        # Otherwise, append the POSTed picture into our data
        data.append(picture)
        return jsonify(picture), 201

    except Exception as e: 
        return jsonify({
            'Message': f'Internal error: {str(e)}. Data not saved.'
        }), 500


######################################################################
# UPDATE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    try:
        picture = request.get_json()
        required_keys = [
            'id',
            'pic_url',
            'event_country',
            'event_state',
            'event_city',
            'event_date'
        ]

        # Validate incoming picture data 
        if not all(key in picture for key in required_keys):
            return jsonify({
                'Message': 'Picture unprocessable. All keys are required'
            }), 422

        # Attempt to find a picture with matching ID
        for idx, pic in enumerate(data):
            if int(pic['id']) == id:
                data[idx] = picture
                
                # Picture match found!
                return jsonify({
                    'Message': 'Picture updated successfully'
                }), 200
        
        return jsonify({'Message': 'Picture not found'}), 404

    except Exception as e:
        return jsonify({'Message': 'Internal server error'}), 500


######################################################################
# DELETE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    try:
        for picture in data:
            if int(picture['id']) == id:
                data.remove(picture)
                return jsonify({
                    'Message': 'Message deleted successfully'
                }), 204 # No content

        # No picture matches the ID
        return jsonify({'Message': 'Picture not found'}), 404

    except Exception as e:
        return jsonify({'Message': 'Internal server error'}), 500
