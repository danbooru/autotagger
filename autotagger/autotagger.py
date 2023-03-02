from fastbook import create_timm_model
import pandas as pd
from pandas import DataFrame
import timm
import sys
import torch
from PIL import Image
import torchvision.transforms as transforms

# https://github.com/fastai/fastai/blob/176accfd5ae929d73d183d596c7155d3a9401f2f/fastai/vision/core.py#L96
# load image and copy to new PIL Image object
# allows removal of fastai dep
def read_image(file):
    im = Image.open(file)
    im.load()
    im = im._new(im.im)
    return im

# take in a single string denoting file path, a single PIL Image instance,
# or a list of either or a combination and handle them using a map-style dataset
class InferenceDataset(torch.utils.data.Dataset):
    def __init__(self, files, transform=None):
        if isinstance(files, (list, tuple)):
            self.files = files
        else:
            self.files = [files]
        
        self.transform = transform
    
    def __len__(self):
        return len(self.files)
        
    def __getitem__(self, index):
        image = self.files[index]
        
        # file path case
        if isinstance(image, str):
            image = Image.open(image)
        
        assert isinstance(image, Image.Image), "Dataset got invalid type, supported types: singular or list of the following: path as a string, PIL Image"
        
        # check if file valid
        image.load()
        
        # fill transparent backgorunds with white and convert to RGB
        image = image.convert("RGBA")
        
        # may not replicate behavior of old impl
        color = (255,255,255)
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[3])
        image = background
        
        if self.transform: image = self.transform(image)
        
        return image
        
class Autotagger:
    def __init__(self, model_path = "models/model.pth", tags_path="data/tags.json"):
    
        # load tags
        self.classes = pd.read_json(tags_path)
        
        # instantiate fastai model
        self.model,_ = create_timm_model("resnet152", len(self.classes), pretrained=False)

        # load weights
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

        # set to eval, script and optimize for inference (~2.5x speedup)
        # trade off init time for faster inference, scripting/tracing is slow
        self.model = self.model.eval()
        
        # depending on what models are used in the future, use either script or trace
        # can't script due to fastai model defn, need to use trace
        #self.model = torch.jit.script(self.model)
        self.model = torch.jit.trace(self.model, torch.randn(1, 3, 224, 224))
        self.model = torch.jit.optimize_for_inference(self.model)
        
    def predict(self, files, threshold=0.01, limit=50, bs=64):
        if not files:
            return
        
        # instantiate dataset using files
        dataset = InferenceDataset(
            files,
            transform=transforms.Compose([
                transforms.Resize((224,224)),
                transforms.ToTensor(),
            ])
        )
        
        # create a dataloader, if calling predict with a large batch,
        # the input is already split into bs chunks, may make more sense to
        # call create a dl with bs of 1, may save memory/reduce latency
        # depending on inputs and use case (autotag with 1 file vs list of files)
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size = bs,
            shuffle=False,
            drop_last=False
        )
        
        for batch in dataloader:
            preds = self.model(batch).sigmoid()
            for scores in preds:
                df = DataFrame({ "tag": self.classes[0], "score": scores })
                df = df[df.score >= threshold].sort_values("score", ascending=False).head(limit)
                tags = dict(zip(df.tag, df.score))
                yield tags
                
            