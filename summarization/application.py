import fastapi
import fastapi.staticfiles
import fastapi.middleware.cors

from .routes import api_router


class SummarizationApplication:
    # we are having this just for development purposes, in production,
    # the vue application is served by the python backend itself, so
    # allowed origins can be an empty array without allowing localhost
    __allowed_origins = ["http://localhost:5173"]
    __allowed_headers: list[str] = ["*"]
    __allowed_methods: list[str] = ["*"]
    __allowed_credentials: bool = True

    @classmethod
    def generate(cls):
        app = fastapi.FastAPI()

        app.add_middleware(
            fastapi.middleware.cors.CORSMiddleware,
            allow_origins=cls.__allowed_origins,
            allow_methods=cls.__allowed_methods,
            allow_headers=cls.__allowed_headers,
            allow_credentials=cls.__allowed_credentials,
        )

        app.include_router(api_router)

        app.mount(
            path="/",
            app=fastapi.staticfiles.StaticFiles(directory="dist/", html=True),
            name="static",
        )

        return app
