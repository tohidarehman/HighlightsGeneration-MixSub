from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routes import apis_router, view_router


class SummarizationApplication:
    # The frontend is served by the python backend itself, so
    # allowed origins can be an empty array without allowing localhost
    __allowed_origins = []
    __allowed_headers: list[str] = ["*"]
    __allowed_methods: list[str] = ["*"]
    __allowed_credentials: bool = True

    @classmethod
    def generate(cls, static_dir="public"):
        app = FastAPI()
        static_app = StaticFiles(directory=static_dir)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=cls.__allowed_origins,
            allow_methods=cls.__allowed_methods,
            allow_headers=cls.__allowed_headers,
            allow_credentials=cls.__allowed_credentials,
        )

        app.mount(path="/public", app=static_app, name="public")
        app.include_router(apis_router)
        app.include_router(view_router)

        return app
