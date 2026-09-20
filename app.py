from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "eventora_advanced_secret"

DATABASE = "eventora.db"


# ---------------- DATABASE ----------------

def db():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "info")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def init_db():
    con = db()

    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'customer',
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        event_type TEXT,
        event_date TEXT,
        location TEXT,
        guests INTEGER,
        budget REAL,
        status TEXT DEFAULT 'Planning',
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS vendors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        location TEXT,
        price REAL,
        rating REAL,
        reviews INTEGER,
        description TEXT,
        image TEXT,
        featured INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id INTEGER,
        vendor_id INTEGER,
        booking_date TEXT,
        status TEXT DEFAULT 'Pending'
    );

    CREATE TABLE IF NOT EXISTS favorites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vendor_id INTEGER,
        UNIQUE(user_id, vendor_id)
    );

    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        title TEXT,
        category TEXT,
        amount REAL
    );

    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vendor_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT
    );
    """)

    # ---------------- USERS ----------------

    if con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        now = datetime.now().isoformat()

        con.executemany(
            """
            INSERT INTO users
            (name, email, password, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "Eventora Admin",
                    "admin@eventora.com",
                    "admin123",
                    "admin",
                    now
                ),
                (
                    "Demo Customer",
                    "demo@eventora.com",
                    "demo123",
                    "customer",
                    now
                )
            ]
        )

    # ---------------- VENDORS ----------------

    if con.execute("SELECT COUNT(*) FROM vendors").fetchone()[0] == 0:

        vendors = [

            (
                "The Grand Courtyard",
                "Venue",
                "Mysuru",
                55000,
                4.9,
                184,
                "Luxury indoor and outdoor celebration venue with stage, lighting and parking.",
                "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Royal Orchid Convention Hall",
                "Venue",
                "Mangaluru",
                45000,
                4.8,
                143,
                "Elegant modern venue for weddings, receptions and corporate events.",
                "https://images.unsplash.com/photo-1507504031003-b417219a0fde?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Gardenia Lake Resort",
                "Venue",
                "Bengaluru",
                75000,
                4.9,
                219,
                "Open-air garden venue with lake views and premium guest spaces.",
                "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Lens & Light Studio",
                "Photography",
                "Mangaluru",
                18000,
                4.7,
                96,
                "Candid wedding photography, cinematic reels and full-day coverage.",
                "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Moments Frame House",
                "Photography",
                "Bengaluru",
                22000,
                4.8,
                127,
                "Editorial portraits, candid stories and highlight films.",
                "https://images.unsplash.com/photo-1507504031003-b417219a0fde?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Flora Decor Studio",
                "Decoration",
                "Mangaluru",
                20000,
                4.6,
                88,
                "Floral stages, entrance styling, table decor and custom themes.",
                "https://images.unsplash.com/photo-1478146896981-b80fe463b330?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Bloom & Gold Events",
                "Decoration",
                "Mysuru",
                28000,
                4.9,
                171,
                "Premium floral installations and elegant luxury event styling.",
                "https://images.unsplash.com/photo-1507504031003-b417219a0fde?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Spice Route Catering",
                "Catering",
                "Mangaluru",
                450,
                4.7,
                112,
                "South Indian, North Indian and buffet menus with live counters.",
                "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=1200&q=85",
                1
            ),

            (
                "Saffron Table",
                "Catering",
                "Bengaluru",
                650,
                4.8,
                139,
                "Premium multi-cuisine catering and curated dessert counters.",
                "https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Rhythm Beats",
                "Music",
                "Mangaluru",
                12000,
                4.5,
                74,
                "DJ, sound, live band coordination and event lighting.",
                "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Glow Studio",
                "Makeup",
                "Mysuru",
                9000,
                4.7,
                102,
                "Bridal makeup, party looks, hair styling and trial sessions.",
                "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Sweet Moments Cakes",
                "Cake",
                "Mangaluru",
                2500,
                4.8,
                91,
                "Custom celebration cakes, dessert tables and themed cupcakes.",
                "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "InviteCraft",
                "Invitations",
                "Online",
                1500,
                4.6,
                66,
                "Digital invitations, RSVP pages, QR invites and print designs.",
                "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Petal & Pearl Florals",
                "Flowers",
                "Mysuru",
                8500,
                4.8,
                83,
                "Bouquets, garlands, aisle flowers and premium floral styling.",
                "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Ride Royale",
                "Transport",
                "Bengaluru",
                6500,
                4.5,
                58,
                "Luxury cars and guest transport packages for special occasions.",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Sparkle & Co. Entertainment",
                "Entertainment",
                "Mysuru",
                15000,
                4.7,
                71,
                "Anchors, performers, games and interactive entertainment.",
                "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Heritage Mehndi Art",
                "Mehndi",
                "Mangaluru",
                5000,
                4.9,
                119,
                "Bridal and festive mehndi artists with custom design consultations.",
                "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=85",
                0
            ),

            (
                "Studio Bloom Hair",
                "Hair Styling",
                "Bengaluru",
                7000,
                4.6,
                63,
                "Bridal hair styling, saree draping and event-ready looks.",
                "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1200&q=85",
                0
            )
        ]

        con.executemany(
            """
            INSERT INTO vendors
            (name, category, location, price, rating, reviews,
             description, image, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            vendors
        )

    # ---------------- DEMO EVENT ----------------

    demo = con.execute(
        "SELECT id FROM users WHERE email='demo@eventora.com'"
    ).fetchone()

    if demo and not con.execute(
        "SELECT id FROM events WHERE user_id=?",
        (demo["id"],)
    ).fetchone():

        now = datetime.now().isoformat()

        con.execute(
            """
            INSERT INTO events
            (user_id, name, event_type, event_date, location,
             guests, budget, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                demo["id"],
                "Aarav & Meera Wedding",
                "Wedding",
                "2026-12-24",
                "Mysuru",
                250,
                100000,
                "Planning",
                now
            )
        )

        eid = con.execute(
            "SELECT last_insert_rowid() id"
        ).fetchone()["id"]

        con.executemany(
            """
            INSERT INTO expenses
            (event_id, title, category, amount)
            VALUES (?, ?, ?, ?)
            """,
            [
                (eid, "Venue advance", "Venue", 18000),
                (eid, "Photography booking", "Photography", 12000),
                (eid, "Floral decor", "Decoration", 8500),
                (eid, "Catering advance", "Catering", 4000)
            ]
        )

        vids = con.execute(
            """
            SELECT id
            FROM vendors
            WHERE name IN
            ('The Grand Courtyard',
             'Lens & Light Studio',
             'Flora Decor Studio')
            ORDER BY id
            """
        ).fetchall()

        for i, v in enumerate(vids[:3]):

            con.execute(
                """
                INSERT INTO bookings
                (user_id, event_id, vendor_id,
                 booking_date, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    demo["id"],
                    eid,
                    v["id"],
                    now,
                    "Confirmed" if i == 0 else "Pending"
                )
            )

        favs = con.execute(
            """
            SELECT id
            FROM vendors
            WHERE featured=1
            ORDER BY rating DESC
            LIMIT 3
            """
        ).fetchall()

        for v in favs:

            try:
                con.execute(
                    """
                    INSERT INTO favorites
                    (user_id, vendor_id)
                    VALUES (?, ?)
                    """,
                    (demo["id"], v["id"])
                )

            except sqlite3.IntegrityError:
                pass

    con.commit()
    con.close()


# ---------------- GLOBAL VARIABLES ----------------

@app.context_processor
def globals():
    return {
        "current_user": session.get("user_name"),
        "role": session.get("role")
    }


# ---------------- HOME ----------------

@app.route("/")
def index():

    con = db()

    featured = con.execute(
        """
        SELECT *
        FROM vendors
        WHERE featured=1
        ORDER BY rating DESC
        LIMIT 6
        """
    ).fetchall()

    categories = con.execute(
        """
        SELECT category, COUNT(*) n
        FROM vendors
        GROUP BY category
        ORDER BY n DESC
        """
    ).fetchall()

    con.close()

    return render_template(
        "index.html",
        featured=featured,
        categories=categories
    )


# ---------------- VENDORS ----------------

@app.route("/vendors")
def vendors():

    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    sort = request.args.get("sort", "rating")

    con = db()

    sql = "SELECT * FROM vendors WHERE 1=1"
    params = []

    if q:

        sql += """
        AND (
            name LIKE ?
            OR category LIKE ?
            OR description LIKE ?
            OR location LIKE ?
        )
        """

        params += [f"%{q}%"] * 4

    if category:

        sql += " AND category=?"
        params.append(category)

    if location:

        sql += " AND location=?"
        params.append(location)

    order = {
        "rating": "rating DESC",
        "price_low": "price ASC",
        "price_high": "price DESC",
        "reviews": "reviews DESC"
    }.get(sort, "rating DESC")

    sql += " ORDER BY " + order

    rows = con.execute(sql, params).fetchall()

    cats = con.execute(
        """
        SELECT DISTINCT category
        FROM vendors
        ORDER BY category
        """
    ).fetchall()

    locations = con.execute(
        """
        SELECT DISTINCT location
        FROM vendors
        ORDER BY location
        """
    ).fetchall()

    con.close()

    return render_template(
        "vendors.html",
        vendors=rows,
        categories=cats,
        locations=locations,
        q=q,
        category=category,
        location=location,
        sort=sort
    )


# ---------------- VENDOR DETAILS ----------------

@app.route("/vendor/<int:vendor_id>")
def vendor(vendor_id):

    con = db()

    v = con.execute(
        "SELECT * FROM vendors WHERE id=?",
        (vendor_id,)
    ).fetchone()

    reviews = con.execute(
        """
        SELECT r.*, u.name
        FROM reviews r
        JOIN users u ON u.id=r.user_id
        WHERE r.vendor_id=?
        ORDER BY r.id DESC
        """,
        (vendor_id,)
    ).fetchall()

    con.close()

    if not v:
        return "Vendor not found", 404

    return render_template(
        "vendor.html",
        vendor=v,
        reviews=reviews
    )


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        con = db()

        try:

            con.execute(
                """
                INSERT INTO users
                (name, email, password, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    request.form["name"],
                    request.form["email"],
                    request.form["password"],
                    "customer",
                    datetime.now().isoformat()
                )
            )

            con.commit()

            flash(
                "Account created successfully.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash(
                "Email already registered.",
                "error"
            )

        finally:

            con.close()

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        con = db()

        u = con.execute(
            """
            SELECT *
            FROM users
            WHERE email=? AND password=?
            """,
            (
                request.form["email"],
                request.form["password"]
            )
        ).fetchone()

        con.close()

        if u:

            session.update(
                user_id=u["id"],
                user_name=u["name"],
                role=u["role"]
            )

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    con = db()

    uid = session["user_id"]

    events = con.execute(
        """
        SELECT *
        FROM events
        WHERE user_id=?
        ORDER BY event_date
        """,
        (uid,)
    ).fetchall()

    bookings = con.execute(
        """
        SELECT b.*,
               v.name vendor_name,
               v.category,
               v.image,
               v.price,
               v.rating
        FROM bookings b
        JOIN vendors v ON v.id=b.vendor_id
        WHERE b.user_id=?
        ORDER BY b.id DESC
        """,
        (uid,)
    ).fetchall()

    favorites = con.execute(
        """
        SELECT v.*
        FROM favorites f
        JOIN vendors v ON v.id=f.vendor_id
        WHERE f.user_id=?
        ORDER BY f.id DESC
        """,
        (uid,)
    ).fetchall()

    expense_rows = con.execute(
        """
        SELECT e.*, x.name event_name
        FROM expenses e
        JOIN events x ON x.id=e.event_id
        WHERE x.user_id=?
        ORDER BY e.id DESC
        """,
        (uid,)
    ).fetchall()

    total_spend = con.execute(
        """
        SELECT COALESCE(SUM(e.amount), 0) total
        FROM expenses e
        JOIN events x ON x.id=e.event_id
        WHERE x.user_id=?
        """,
        (uid,)
    ).fetchone()["total"]

    total_budget = con.execute(
        """
        SELECT COALESCE(SUM(budget), 0) total
        FROM events
        WHERE user_id=?
        """,
        (uid,)
    ).fetchone()["total"]

    upcoming = con.execute(
        """
        SELECT *
        FROM events
        WHERE user_id=?
        AND event_date >= date('now')
        ORDER BY event_date
        LIMIT 1
        """,
        (uid,)
    ).fetchone()

    categories = con.execute(
        """
        SELECT category,
               COALESCE(SUM(amount), 0) total
        FROM expenses e
        JOIN events x ON x.id=e.event_id
        WHERE x.user_id=?
        GROUP BY category
        ORDER BY total DESC
        """,
        (uid,)
    ).fetchall()

    status_rows = con.execute(
        """
        SELECT status, COUNT(*) n
        FROM bookings
        WHERE user_id=?
        GROUP BY status
        """,
        (uid,)
    ).fetchall()

    con.close()

    remaining = max(
        total_budget - total_spend,
        0
    )

    progress = (
        round((total_spend / total_budget) * 100)
        if total_budget
        else 0
    )

    return render_template(
        "dashboard.html",
        events=events,
        bookings=bookings,
        favorites=favorites,
        expense_rows=expense_rows,
        total_spend=total_spend,
        total_budget=total_budget,
        remaining=remaining,
        progress=min(progress, 100),
        upcoming=upcoming,
        categories=categories,
        status_rows=status_rows
    )


# ---------------- CREATE EVENT ----------------

@app.route("/create-event", methods=["POST"])
@login_required
def create_event():

    con = db()

    con.execute(
        """
        INSERT INTO events
        (user_id, name, event_type, event_date,
         location, guests, budget, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            request.form["name"],
            request.form["event_type"],
            request.form["event_date"],
            request.form["location"],
            request.form["guests"],
            request.form["budget"],
            datetime.now().isoformat()
        )
    )

    con.commit()
    con.close()

    flash(
        "Event created. Start planning!",
        "success"
    )

    return redirect(url_for("dashboard"))


# ---------------- BOOK VENDOR ----------------

@app.route("/book/<int:vendor_id>", methods=["POST"])
@login_required
def book(vendor_id):

    con = db()

    event = con.execute(
        """
        SELECT id
        FROM events
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    if not event:

        con.close()

        flash(
            "Create an event before booking a vendor.",
            "error"
        )

        return redirect(url_for("dashboard"))

    con.execute(
        """
        INSERT INTO bookings
        (user_id, event_id, vendor_id,
         booking_date, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            event["id"],
            vendor_id,
            datetime.now().isoformat(),
            "Pending"
        )
    )

    con.commit()
    con.close()

    flash(
        "Booking request sent to the vendor.",
        "success"
    )

    return redirect(
        url_for(
            "vendor",
            vendor_id=vendor_id
        )
    )


# ---------------- FAVORITE ----------------

@app.route("/favorite/<int:vendor_id>")
@login_required
def favorite(vendor_id):

    con = db()

    try:

        con.execute(
            """
            INSERT INTO favorites
            (user_id, vendor_id)
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                vendor_id
            )
        )

    except sqlite3.IntegrityError:

        con.execute(
            """
            DELETE FROM favorites
            WHERE user_id=? AND vendor_id=?
            """,
            (
                session["user_id"],
                vendor_id
            )
        )

    con.commit()
    con.close()

    return redirect(
        request.referrer or url_for("vendors")
    )


# ---------------- REVIEW ----------------

@app.route("/review/<int:vendor_id>", methods=["POST"])
@login_required
def review(vendor_id):

    con = db()

    con.execute(
        """
        INSERT INTO reviews
        (user_id, vendor_id, rating,
         comment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            vendor_id,
            int(request.form["rating"]),
            request.form["comment"],
            datetime.now().isoformat()
        )
    )

    con.commit()

    avg = con.execute(
        """
        SELECT AVG(rating) a,
               COUNT(*) n
        FROM reviews
        WHERE vendor_id=?
        """,
        (vendor_id,)
    ).fetchone()

    con.execute(
        """
        UPDATE vendors
        SET rating=?,
            reviews=reviews+1
        WHERE id=?
        """,
        (
            round(avg["a"], 1),
            vendor_id
        )
    )

    con.commit()
    con.close()

    return redirect(
        url_for(
            "vendor",
            vendor_id=vendor_id
        )
    )


# ---------------- EXPENSE ----------------

@app.route("/expense", methods=["POST"])
@login_required
def expense():

    con = db()

    event_id = request.form.get("event_id")

    if not event_id:

        event = con.execute(
            """
            SELECT id
            FROM events
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        event_id = (
            event["id"]
            if event
            else None
        )

    if event_id:

        owner = con.execute(
            """
            SELECT id
            FROM events
            WHERE id=? AND user_id=?
            """,
            (
                event_id,
                session["user_id"]
            )
        ).fetchone()

        if owner:

            con.execute(
                """
                INSERT INTO expenses
                (event_id, title, category, amount)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event_id,
                    request.form["title"],
                    request.form["category"],
                    request.form["amount"]
                )
            )

            con.commit()

            flash(
                "Expense added to your planner.",
                "success"
            )

        else:

            flash(
                "Please choose one of your own events.",
                "error"
            )

    else:

        flash(
            "Create an event before adding expenses.",
            "error"
        )

    con.close()

    return redirect(
        url_for("dashboard")
    )


# ---------------- DELETE EXPENSE ----------------

@app.route(
    "/expense/delete/<int:expense_id>",
    methods=["POST"]
)
@login_required
def delete_expense(expense_id):

    con = db()

    con.execute(
        """
        DELETE FROM expenses
        WHERE id=?
        AND event_id IN
        (
            SELECT id
            FROM events
            WHERE user_id=?
        )
        """,
        (
            expense_id,
            session["user_id"]
        )
    )

    con.commit()
    con.close()

    flash(
        "Expense removed.",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# ---------------- ADMIN ----------------

@app.route("/admin")
@login_required
def admin():

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    con = db()

    stats = [
        con.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0],

        con.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0],

        con.execute(
            "SELECT COUNT(*) FROM vendors"
        ).fetchone()[0],

        con.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]
    ]

    recent = con.execute(
        """
        SELECT b.*,
               u.name user_name,
               v.name vendor_name
        FROM bookings b
        JOIN users u ON u.id=b.user_id
        JOIN vendors v ON v.id=b.vendor_id
        ORDER BY b.id DESC
        LIMIT 12
        """
    ).fetchall()

    con.close()

    return render_template(
        "admin.html",
        stats=stats,
        recent=recent
    )


# ---------------- API ----------------

@app.route("/api/vendors")
def api_vendors():

    con = db()

    rows = con.execute(
        """
        SELECT id,
               name,
               category,
               location,
               price,
               rating,
               image
        FROM vendors
        """
    ).fetchall()

    con.close()

    return jsonify(
        [dict(x) for x in rows]
    )


# ==================================================
# IMPORTANT FOR RENDER / GUNICORN
# ==================================================

# Initialize database when Gunicorn starts.
# This creates all tables and demo data on Render.
init_db()


if __name__ == "__main__":

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )
