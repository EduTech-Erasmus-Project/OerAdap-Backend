#application = get_asgi_application()
''' 
ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    # url(r"^api/adapter/(?P<tag>[\w.@+-]+)/$", VideoConsumer),
                    url(r"^api/adapter/video/progress/(?P<tag>[\w.@+-]+)/$", VideoConsumer.as_asgi()),
                ]
            )
        )
    )

})
'''