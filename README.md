# Ad-Event-Stream
This is an advertising system demo using [faust-streaming](https://github.com/faust-streaming/faust).

## Diagram
![diagram](docs/diagrams_image.png)
- The actual implementation differs slightly from the diagram above.
  - To simulate easily, an event is produced by faust timer.

## Run
```shell
$ docker-compose up -d
$ faust -A main worker -l info
```