import typer

app = typer.Typer()


@app.command()
def ls():
    ...


if __name__ == "__main__":
    app()
