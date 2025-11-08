from deepface import DeepFace

result = DeepFace.analyze(
    img_path = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img1.jpg",
    actions = ['emotion']
)

print(result)
