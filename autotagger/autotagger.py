from fastbook import *
from pandas import read_csv
import timm

class Autotagger:
    def __init__(self, model_path="models/model.pth", data_path="test/tags.csv.gz", tags_path="data/tags.json"):
        self.model_path = model_path
        self.learn = self.init_model(data_path=data_path, tags_path=tags_path, model_path=model_path)

    def init_model(self, model_path="model/model.pth", data_path="test/tags.csv.gz", tags_path="data/tags.json"):
        df = read_csv(data_path)
        vocab = json.load(open(tags_path))

        dblock = DataBlock(
            blocks=(ImageBlock, MultiCategoryBlock(vocab=vocab)),
            get_x = lambda df: Path("test") / df["filename"],
            get_y = lambda df: df["tags"].split(" "),
            item_tfms = Resize(224, method = ResizeMethod.Squish),
            batch_tfms = [RandomErasing()]
        )

        dls = dblock.dataloaders(df)
        learn = vision_learner(dls, "resnet152", pretrained=False)
        model_file = open(model_path, "rb")
        learn.load(model_file, with_opt=False)

        return learn

    def predict(self, path, threshold=0.01, limit=50):
        with self.learn.no_bar(), self.learn.no_logging():
            pred = self.learn.predict(path)
            scores = [score.item() for score in pred[2]]
            results = { tag : score for (tag, score) in zip(self.learn.dls.vocab, scores) if score >= threshold }
            results = sorted(results.items(), key = lambda x: -x[1])
            return dict(results[:limit])
