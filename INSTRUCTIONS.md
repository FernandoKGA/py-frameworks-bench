# Instruções

Para construir a imagem base: `docker build . -t benchbase:latest`

Para limpeza das imagens caso algum erro, troque o texto no `grep` para o app que gostaria:
```sh
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep '^fastapi_app' | awk '{print $2}' | xargs -r docker rmi
```

Para rodar o programa:
```sh
./run.py --use-good-versions --rounds N
```