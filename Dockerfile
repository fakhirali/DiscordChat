#FROM nvidia/cuda:latest
#FROM nvidia/cuda:11.5.0-base
#FROM nvidia/cuda
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST 0.0.0.0

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget \
    ocl-icd-opencl-dev opencl-headers clinfo \
    libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

COPY . .

# setting build related env vars
ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1


WORKDIR ./
COPY . .
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y libgl1-mesa-glx

RUN pip install -r freeze.txt

RUN python3 -m pip install --upgrade pip pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette pydantic-settings starlette-context

RUN CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python

CMD ["bash", "run.sh"]