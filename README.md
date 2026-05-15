# Image Based Product Search

A Django web application that uses a ResNet50 ONNX model to classify images and return top product matches with Google search links.

## Features

- Upload an image or provide an image URL
- Returns top 5 predicted labels with confidence scores
- Links each result to a Google search
- Rate limiting per IP address

## Project Structure

```
imgsearch/
├── imgsearch/          # Django project settings
├── predictor/          # Views, URLs, middleware
└── utlities/
    ├── text_classifier.py  # Model inference logic
    └── models/             # Downloaded ONNX model stored here
```

## Setup

```bash
git clone https://github.com/ramimK0bir/image_based_product_search.git
cd cd image_based_product_search
pip install -r imgsearch/requirements.txt
python imgsearch/manage.py migrate
python imgsearch/manage.py runserver
```

The model will be downloaded automatically on first run into `utlities/models/`.

## Usage

- Visit `http://127.0.0.1:8000/`
- Upload an image file or paste an image URL
- View top predictions with confidence scores

## License

MIT License — see [LICENSE.txt](LICENSE.txt)

## Author

[userAnonymous](https://github.com/userAnonymous)
