import torch
import torch.nn as nn

print("Torch version:", torch.__version__)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.linear = nn.Linear(10, 1)

    def forward(self, x):
        return self.linear(x)

model = Net()
print("Initialized model:", model)
