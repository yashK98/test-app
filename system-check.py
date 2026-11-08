import torch
import transformers

print("Torch Version :: ", torch.__version__)
print("Transformers Version :: ", transformers.__version__)
print("CUDA Available :: ", torch.cuda.is_available())
print("CPU Available :: ", torch.backends.cpu.get_cpu_capability())