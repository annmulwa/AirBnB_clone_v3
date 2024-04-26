#!/usr/bin/python3
"""
Creates reviews
"""
from flask import jsonify, abort, request
from models.place import Place
from models.review import Review
from models.user import User
from models import storage
from api.v1.views import app_views


@app_views.route('/places/<place_id>/reviews', strict_slashes=False)
def get_all_reviews(place_id):
    """
    Retrieves the list of all Review objects of a Place
    """
    place = storage.get(Place, place_id)
    if not place:
        return abort(404)
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', strict_slashes=False)
def get_review(review_id):
    """
    Retrieves a Review object
    """
    review = storage.get(Review, review_id)

    if review:
        return jsonify(review.to_dict())
    else:
        return abort(404)


@app_views.route('/reviews/<review_id>', methods=['DELETE'], strict_slashes=False)  # noqa
def delete_review(review_id):
    """
    Deletes a Review object
    """
    review = storage.get(Review, review_id)

    if review:
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    else:
        return abort(404)


@app_views.route('/places/<place_id>/reviews',
                 methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """
    Creates a Review object
    """
    place = storage.get(Place, place_id)
    if not place:
        return abort(404)
    if not request.get_json():
        return abort(400, 'Not a JSON')
    data = request.get_json()
    if 'user_id' not in data:
        return abort(400, 'Missing user_id')
    if 'text' not in data:
        return abort(400, 'Missing text')
    user = storage.get(User, data['user_id'])
    if not user:
        return abort(404)
    data['place_id'] = place_id
    review = Review(**data)
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)
def update_review(review_id):
    """
    Updates a Review object
    """
    if request.content_type != 'application/json':
        return abort(400, 'Not a JSON')
    review = storage.get(Review, review_id)
    if review:
        if not request.get_json():
            return abort(400, 'Not a JSON')
        data = request.get_json()
        ignore_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']

        for key, value in data.items():
            if key not in ignore_keys:
                setattr(review, key, value)
        review.save()
        return jsonify(review.to_dict()), 200
    else:
        return abort(404)
