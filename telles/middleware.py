from django.shortcuts import redirect
from django.urls import reverse


class EmailVerificationMiddleware:
    """
    学生ユーザーがメールアドレスを登録していない場合、
    メールアドレス登録画面以外へのアクセスをブロックするミドルウェア
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 許可されるURL名のリスト
        allowed_url_names = [
            'telles:email_registration',
            'telles:email_verification',
            'telles:device_verification',
            'telles:resend_verification_code',
            'telles:student_login',
            'telles:teacher_login',
            'telles:teacher_signup',
            'telles:login_selection',  # ルートパス
            'telles:logout',
            'telles:logout_complete',
        ]

        # 許可されたパスのリスト（名前から解決）
        allowed_paths = []
        for name in allowed_url_names:
            try:
                allowed_paths.append(reverse(name))
            except:
                pass

        # ユーザーがログインしていて、学生である場合のみチェック
        if request.user.is_authenticated and hasattr(request.user, 'is_student') and request.user.is_student:
            # メールアドレス未登録 or 未認証の場合
            if not request.user.email or not request.user.email_verified:
                # staticファイルとadmin、および許可パス以外へのアクセスをブロック
                if not any(request.path.startswith(path) for path in allowed_paths) and \
                   not request.path.startswith('/static/') and \
                   not request.path.startswith('/admin/'):
                    return redirect('telles:email_registration')
        
        response = self.get_response(request)
        return response
