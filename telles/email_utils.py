import random
import string
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailVerificationCode, TrustedDevice


def generate_verification_code():
    """6桁のランダムな数字コードを生成"""
    return ''.join(random.choices(string.digits, k=6))


def generate_device_token():
    """64文字のランダムなデバイストークンを生成"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))


def send_verification_email(user, code):
    """
    認証コードをメールで送信
    
    Args:
        user: CustomUserインスタンス
        code: 6桁の認証コード
    
    Returns:
        bool: 送信成功ならTrue
    """
    subject = '【Telles】認証コードのお知らせ'
    message = f'''
こんにちは、{user.username} さん

Tellesへのログインに必要な認証コードは以下の通りです:

認証コード: {code}

このコードの有効期限は10分間です。
もしこのメールに心当たりがない場合は、無視してください。

---
Telles 出欠管理システム
'''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def create_verification_code(user):
    """
    新しい認証コードを生成してデータベースに保存
    
    Args:
        user: CustomUserインスタンス
    
    Returns:
        EmailVerificationCode: 作成されたコードオブジェクト
    """
    code = generate_verification_code()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    verification_code = EmailVerificationCode.objects.create(
        user=user,
        code=code,
        expires_at=expires_at
    )
    
    return verification_code


def create_trusted_device(user, user_agent=''):
    """
    新しい信頼済みデバイスを作成
    
    Args:
        user: CustomUserインスタンス
        user_agent: ブラウザのUser-Agent文字列
    
    Returns:
        TrustedDevice: 作成されたデバイスオブジェクト
    """
    device_token = generate_device_token()
    expires_at = timezone.now() + timedelta(days=90)  # 3ヶ月
    
    trusted_device = TrustedDevice.objects.create(
        user=user,
        device_token=device_token,
        expires_at=expires_at,
        user_agent=user_agent
    )
    
    return trusted_device


def verify_code(user, code):
    """
    認証コードを検証
    
    Args:
        user: CustomUserインスタンス
        code: 入力された認証コード
    
    Returns:
        tuple: (成功フラグ, エラーメッセージ)
    """
    try:
        verification = EmailVerificationCode.objects.filter(
            user=user,
            code=code,
            is_used=False
        ).order_by('-created_at').first()
        
        if not verification:
            return False, "認証コードが正しくありません。"
        
        if not verification.is_valid():
            return False, "認証コードの有効期限が切れています。"
        
        # コードを使用済みにする
        verification.is_used = True
        verification.save()
        
        return True, None
        
    except Exception as e:
        return False, f"エラーが発生しました: {str(e)}"


def get_device_token_from_request(request):
    """
    リクエストからデバイストークンを取得
    
    Args:
        request: HttpRequestオブジェクト
    
    Returns:
        str or None: デバイストークン
    """
    return request.COOKIES.get('device_token')


def check_trusted_device(user, device_token):
    """
    デバイストークンが有効かチェック
    
    Args:
        user: CustomUserインスタンス
        device_token: デバイストークン文字列
    
    Returns:
        bool: 有効ならTrue
    """
    if not device_token:
        return False
    
    try:
        device = TrustedDevice.objects.get(
            user=user,
            device_token=device_token
        )
        return device.is_valid()
    except TrustedDevice.DoesNotExist:
        return False
