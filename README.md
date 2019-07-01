# seal_k-means

### Setting up Docker image for PySEAL
```
cd PySEAL
docker build -t seal-save -f Dockerfile .
```

### Running Jupyter notebook in Docker image

```
docker run -it -p 8888:8888 seal-save bash
root@4bb63b8f3776:/SEAL# jupyter notebook --ip 0.0.0.0 --no-browser --allow-root 
```

