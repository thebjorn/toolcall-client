# -*- coding: utf-8 -*-

from django import http, shortcuts
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .apiutils import send_result_token, ToolCallError, error_response


@login_required
@csrf_exempt
def run_adding_test(request):
    """Minimalist example of show a form on screen and redirect on a post.
       This is intended to

    """
    if request.method == 'POST':
        correct = request.POST.get('answer') == 'ja'
        try:
            send_result_token(request, correct)
        except ToolCallError as toolerr:
            return error_response(toolerr)

        return shortcuts.render_to_response('toolcall_client/close-window.html')

    # show exam..
    return http.HttpResponse(u"""
    <!doctype html>
    <head>
    </head>
    <body>
        <form action="." method="POST">
            <pre>5 + 2 = 7</pre>
            <input type="submit" name=answer value="ja">
            <input type="submit" name=answer value="nei">
        </form>
    </body>
    </html>
    """)


