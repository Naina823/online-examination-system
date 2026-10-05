from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from app.extensions import db
from app.models.user import User

from app.auth.forms import (
    RegistrationForm,
    LoginForm
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ============================================================
# REGISTER
# ============================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        # Check whether username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:

            flash(
                "Username or email already exists.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )


        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            role=form.role.data
        )


        # Hash password
        user.set_password(
            form.password.data
        )


        # Save user
        db.session.add(user)
        db.session.commit()


        flash(
            "Account created successfully. Please login.",
            "success"
        )


        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "auth/register.html",
        form=form
    )


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()


    # --------------------------------------------------------
    # LOGIN FORM SUBMITTED
    # --------------------------------------------------------

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()


        # Check username and password
        if user and user.check_password(
            form.password.data
        ):

            # Log in the user
            login_user(user)


            flash(
                "Login successful.",
                "success"
            )


            # Student → Student Dashboard
            if user.role == "student":

                return redirect(
                    url_for("student.dashboard")
                )


            # Teacher → Teacher Dashboard
            elif user.role == "teacher":

                return redirect(
                    url_for("teacher.dashboard")
                )


            # Unknown role
            flash(
                "Invalid user role.",
                "danger"
            )

            return redirect(
                url_for("main.home")
            )


        # Invalid credentials
        flash(
            "Invalid username or password.",
            "danger"
        )


    # --------------------------------------------------------
    # IMPORTANT:
    # We intentionally DO NOT redirect an already logged-in
    # user here.
    #
    # This means clicking Login always opens the login page.
    # --------------------------------------------------------

    return render_template(
        "auth/login.html",
        form=form
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout")
def logout():

    logout_user()


    flash(
        "You have been logged out.",
        "info"
    )


    return redirect(
        url_for("main.home")
    )