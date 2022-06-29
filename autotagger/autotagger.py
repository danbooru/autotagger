from fastbook import *
from pandas import DataFrame, read_csv
import timm
import sys

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

    def predict(self, files, threshold=0.01, limit=50, bs=64):
        with self.learn.no_bar(), self.learn.no_logging():
            def create_image(file):
                try:
                    return PILImage.create(file)
                except:
                    print("skipped file " + file.name, file=sys.stderr)
                    return None
            images = [create_image(file) for file in files]
            files = [files[i] for i in range(len(files)) if images[i] != None]
            images = [image for image in images if image != None]
            dl = self.learn.dls.test_dl(images, bs=bs)
            batch, _ = self.learn.get_preds(dl=dl)

            for scores, f in zip(batch, files):
                df = DataFrame({ "tag": self.learn.dls.vocab, "score": scores })
                df = df[df.score >= threshold].sort_values("score", ascending=False).head(limit)
                tags = dict(zip(df.tag, df.score))
                yield f.name, tags
