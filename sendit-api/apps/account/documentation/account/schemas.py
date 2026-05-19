from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.utils import extend_schema, extend_schema_view ,OpenApiExample,OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from apps.account.serializers import ( 
  UserSerializer, LoginSerializer, LogoutSerializer, OTPSerializer,EmailSerializer,PasswordResetSerializer,
  ProfileSerializer, GoogleLoginSerializer,VerificationSerializer,ReviewVerificationSerializer  )
from apps.account.documentation.account.docstrings import (
    REGISTER_USER_DESCRIPTION, LOGIN_VIEW_DESCRIPTION, LOGIN_USER_200_OK, LOGIN_USER_400_BAD_REQUEST, LOGOUT_USER_DESCRIPTION,
    REGISTER_USER_CREATED, REGISTER_USER_BAD_REQUEST, VERIFY_EMAIL_OTP_DESCRIPTION, VERIFY_EMAIL_OTP_FAILURE_RESPONSE,
    VERIFY_EMAIL_OTP_SUCCESS_RESPONSE, VERIFY_EMAIL_OTP_USER_NOT_FOUND_RESPONSE, RESEND_OTP_DESCRIPTION, RESEND_OTP_SUCCESS_RESPONSE,
    RESEND_OTP_NOT_FOUND_RESPONSE, RESEND_OTP_ERROR_RESPONSE, PROFILE_REQUEST,  PROFILE_204_RESPONSE, PROFILE_400_RESPONSE, 
    PROFILE_404_RESPONSE, TOKEN_REFRESH_200_OK, TOKEN_REFRESH_DESCRIPTION,TOKEN_REFRESH_400_BAD_REQUEST, 
    VERIFICATION_LIST_200, VERIFICATION_CREATE_201,VERIFICATION_CREATE_400,VERIFICATION_REVIEW_200,VERIFICATION_REVIEW_400
)


register_user_doc = extend_schema(
    methods=['POST'],
    summary='User registration endpoint.',
    description=REGISTER_USER_DESCRIPTION,
    request=UserSerializer,
    responses={
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    examples=[REGISTER_USER_CREATED, REGISTER_USER_BAD_REQUEST],
    tags=['Authentication']
)


email_verify_otp_doc = extend_schema(
    methods=['POST'],
    summary='Verify email with OTP',
    description=VERIFY_EMAIL_OTP_DESCRIPTION,
    request=OTPSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
    examples=[VERIFY_EMAIL_OTP_SUCCESS_RESPONSE,
              VERIFY_EMAIL_OTP_FAILURE_RESPONSE, VERIFY_EMAIL_OTP_USER_NOT_FOUND_RESPONSE],
    tags=['Authentication']
)


resend_email_otp_doc = extend_schema(
    methods=['POST'],
    summary='Resend OTP for email verification',
    description=RESEND_OTP_DESCRIPTION,
    request=EmailSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT
    },
    examples=[
        RESEND_OTP_SUCCESS_RESPONSE,
        RESEND_OTP_NOT_FOUND_RESPONSE,
        RESEND_OTP_ERROR_RESPONSE
    ],
    tags=['Authentication']
)


login_user_doc = extend_schema(
    methods=['POST'],
    summary='User login endpoint.',
    description=LOGIN_VIEW_DESCRIPTION,
    request=LoginSerializer,
    responses={
      200:OpenApiTypes.OBJECT,
      400:OpenApiTypes.OBJECT},
    examples=[LOGIN_USER_200_OK,LOGIN_USER_400_BAD_REQUEST],
    tags=['Authentication']

)

refresh_token_doc = extend_schema_view(
    post=extend_schema(
        methods=['POST'],
        summary='Token refresh endpoint to get new access token',
        description=TOKEN_REFRESH_DESCRIPTION,
        request=LogoutSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[TOKEN_REFRESH_200_OK, TOKEN_REFRESH_400_BAD_REQUEST],
        tags=['Token']
    )
)

logout_user_doc = extend_schema(
    methods=['POST'],
    summary='Logout user. You must be logged in to access this endpoint',
    description=LOGOUT_USER_DESCRIPTION,
    request=LogoutSerializer,
    responses={
        205: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Logout Response',
            value={'message': 'Logout successful'},
            response_only=True,
            status_codes=['205'],
        ),
        OpenApiExample(
            'Error Response',
            value={'error': 'Token is invalid or expired'},
            response_only=True,
            status_codes=['400'],
        ),
    ]
)


password_reset_otp_doc = extend_schema(
    summary="Request Password Reset send reset OTP and url to mail ",
    description=(
        "Public endpoint to request a password reset OTP. "
        "Accepts an email address and sends an OTP to the user if the email is associated with an account. "
        "Response is the same regardless of whether the email exists (for security)."
    ),
    request=EmailSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Successful request (email exists or not)",
            value={"message": "Password reset OTP sent if email exists. Check email and follow the link"},
            status_codes=["200"],
            response_only=True
        ),
        OpenApiExample(
        '500 INTERNAL SERVER ERROR',
        summary='Error generating OTP or sending email',
        description='There was an internal error while trying to reset password with OTP.',
        value={
            "message": "Failed to resend OTP: <error_message> either mail not send "
        },
        status_codes=['500'],
        response_only=True
)
        
    ],
    tags=["Authentication & Password Reset"],
)


password_reset_verify = extend_schema(
    summary="Verify OTP and reset password",
    description="""
    Public endpoint to verify a one-time password (OTP) sent to a user's email address for password reset.
    
    The user provides:
    - `email` (as query parameter),
    - `otp`,
    - `new_password`,
    - `confirm_password` (inside the request body).

    If the OTP is valid and matches the one stored for the given email, the user's password is updated.

    Responses:
    - `200 OK` - Password successfully updated.
    - `400 Bad Request` - Invalid or expired OTP, or validation errors.
    - `404 Not Found` - User with the given email does not exist.
    """,
    request=PasswordResetSerializer,
    responses={
        200: OpenApiResponse(
            description="Password updated successfully. Kindly login.",
            examples=[
                {
                    "value": {"message": "Password updated successfully. Kindly login"},
                    "summary": "Password successfully reset"
                }
            ]
        ),
        400: OpenApiResponse(
            description="OTP invalid or expired.",
            examples=[
                {
                    "value": {"message": "Invalid or expired OTP"},
                    "summary": "Invalid OTP"
                }
            ]
        ),
        404: OpenApiResponse(
            description="User not found for provided email.",
            examples=[
                {
                    "value": {"message": "User not found"},
                    "summary": "User not found"
                }
            ]
        ),
    },
    tags=["Authentication & Password Reset"]
)


profile_doc = extend_schema_view(
    get=extend_schema(
        summary='Retrieve a profile by ID.',
        description='Endpoint to retrieve a profile by their unique ID by the user or admin. User must be authenticated(logged in ) to view their profile',
        responses={404:OpenApiTypes.OBJECT},
        examples=[PROFILE_404_RESPONSE],
        tags=['Profiles'],
    ),
    patch=extend_schema(
        summary='Partially update a profile.',
        description='Endpoint to partially update profile details. Include the field to be updated field alone in the body. Must be authenticated to perform the action',
        request=OpenApiTypes.OBJECT,
        responses={200: ProfileSerializer},
        examples=[PROFILE_REQUEST],
        tags=['Profiles'],
    ),
    delete=extend_schema(
        summary='Delete a profile to remove the user.',
        description='Endpoint to remove a profile by ID.',
        responses={
            204: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT
        },
        examples=[PROFILE_204_RESPONSE, PROFILE_404_RESPONSE],
        tags=['Profiles'],
    ),
)


get_me_doc = extend_schema(
    methods=['GET'],
    summary='Retrieve current user profile',
    description=(
        "Returns the profile information of the currently authenticated user. "
        "Requires a valid JWT access token in the Authorization header.\n\n"
        "Example header:\n"
        "`Authorization: Bearer <access_token>`"
    ),
    request=None,
    responses={
        200: ProfileSerializer,
        401: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Unauthorized',
            value={
                "detail": "Authentication credentials were not provided."
            },
            response_only=True,
            status_codes=['401'],
        ),
        OpenApiExample(
            'Profile Not Found',
            value={
                "status": "profile not found!"
            },
            response_only=True,
            status_codes=['404'],
        ),
    ]
)

google_login_doc = extend_schema(
  
    methods=['POST'],
    summary='Login or register user via Google OAuth',
    description=(
        "Authenticate a user using Google. "
        "Accepts either an `id_token` (SPA flow) or an authorization `code` (OAuth flow). "
        "Returns JWT access and refresh tokens upon successful authentication."
    ),
    request=GoogleLoginSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Google Login with ID Token',
            value={
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ij..."
            },
            request_only=True,
        ),
        OpenApiExample(
            'Google Login with Authorization Code',
            value={
                "code": "4/0AX4XfWg..."
            },
            request_only=True,
        ),
        OpenApiExample(
            'Successful Response',
            value= {
            'status': 'Success',
            'message': 'Authenticated successfully!',
            'data': {
            "id":"uuid","first_name":"string","last_name":"string","email":"string"},
            'token': {
                "access_token": "jwt-access-token",
                "refresh_token": "jwt-refresh-token",
            }},
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            'Invalid Token/Code',
            value={
                "error": "Invalid Google token or authorization code"
            },
            response_only=True,
            status_codes=['400'],
        ),
    ]
)


google_auth_config_doc = extend_schema(
    methods=['GET'],
    summary='Retrieve Google OAuth client configuration',
    description=(
        "Returns the Google OAuth client ID required to initialize Google authentication "
        "on the frontend. This endpoint is public and does not require authentication."
    ),
    request=None,
    responses={
        200: OpenApiTypes.OBJECT,
    },
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Successful Response',
            value={
                "client_id": "1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com"
            },
            response_only=True,
            status_codes=['200'],
        ),
    ]
)


profile_view_doc = extend_schema(
    methods=['GET', 'PATCH', 'DELETE'],
    summary='Retrieve, update or delete a user profile',
    description=(
        "This endpoint allows an authenticated user to retrieve, update, or delete their profile. "
        "Admins can access any user's profile, while normal users can only access their own.\n\n"
        "Use the `user_id` (UUID) in the URL path to identify the profile."
    ),
    request=ProfileSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        204: None,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
    tags=['Profile'],
    examples=[
        # 🔹 GET SUCCESS
        OpenApiExample(
            'Successful Profile Retrieval',
            value={
                "status": "success",
                "data": {
                    "id": "uuid",
                    "user": {
                        "id": "uuid",
                        "email": "user@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    },
                    "bio": "Software developer",
                    "avatar": "https://res.cloudinary.com/.../avatar.jpg",
                    "is_verified": False
                }
            },
            response_only=True,
            status_codes=['200'],
        ),

        # 🔹 PATCH REQUEST
        OpenApiExample(
            'Update Profile Request',
            value={
                "bio": "Updated bio",
                "first_name": "John",
                "last_name": "Doe"
            },
            request_only=True,
        ),

        # 🔹 PATCH RESPONSE
        OpenApiExample(
            'Successful Profile Update',
            value={
                "status": "success",
                "message": "successfully updated",
                "data": {
                    "id": "uuid",
                    "bio": "Updated bio"
                }
            },
            response_only=True,
            status_codes=['200'],
        ),

        # 🔹 FORBIDDEN
        OpenApiExample(
            'Unauthorized Access',
            value={
                "detail": "You do not have permission to perform this action."
            },
            response_only=True,
            status_codes=['403'],
        ),

        # 🔹 NOT FOUND
        OpenApiExample(
            'Profile Not Found',
            value={
                "detail": "Not found."
            },
            response_only=True,
            status_codes=['404'],
        ),

        # 🔹 DELETE RESPONSE
        OpenApiExample(
            'Successful Deletion',
            value=None,
            response_only=True,
            status_codes=['204'],
        ),
    ]
)



verification_doc = extend_schema_view(

    list=extend_schema(
        summary="List verifications",
        description=(
            "Retrieve verifications. ადმინისტ\n"
            "- Admin users see all verifications.\n"
            "- Regular users see only their own."
        ),
        responses={200: OpenApiTypes.OBJECT},
        examples=[VERIFICATION_LIST_200],
        tags=["Verifications"],
    ),

    retrieve=extend_schema(
        summary="Retrieve a verification",
        description="Get details of a specific verification by ID.",
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
        tags=["Verifications"],
    ),

    create=extend_schema(
        summary="Submit verification",
        description=(
            "Submit verification documents. The verification will be created "
            "and linked to the authenticated user's profile."
        ),
        request=VerificationSerializer,
        responses={201: VerificationSerializer, 400: OpenApiTypes.OBJECT},
        examples=[VERIFICATION_CREATE_201, VERIFICATION_CREATE_400],
        tags=["Verifications"],
    ),

    partial_update=extend_schema(
        summary="Update verification",
        description="Partially update a verification record.",
        request=VerificationSerializer,
        responses={200: VerificationSerializer},
        tags=["Verifications"],
    ),

    destroy=extend_schema(
        summary="Delete verification",
        description="Delete a verification record.",
        responses={204: OpenApiTypes.OBJECT},
        tags=["Verifications"],
    ),
)

review_verification_doc = extend_schema(
    summary="Review verification (Admin only)",
    description=(
        "Allows an admin to approve or reject a verification.\n\n"
        "- Sets `is_verified`\n"
        "- Optionally adds a note(compulsory during un_verified)\n"
        "- Updates profile verification status automatically"
    ),
    request=OpenApiTypes.OBJECT,
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    examples=[VERIFICATION_REVIEW_200, VERIFICATION_REVIEW_400],
    tags=["Verifications"],
)


