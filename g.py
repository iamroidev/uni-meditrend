from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor

DARK_NAVY   = HexColor("#0D1B2A")
ACCENT_BLUE = HexColor("#1B4F72")
MID_BLUE    = HexColor("#2E86C1")
LIGHT_BLUE  = HexColor("#D6EAF8")
PALE_GRAY   = HexColor("#F4F6F8")
BORDER_GRAY = HexColor("#AEB6BF")
WHITE       = colors.white
BLACK       = colors.black
GOLD        = HexColor("#F0B429")
DARK_TEXT   = HexColor("#1A1A2E")
GREEN_DARK  = HexColor("#1A5276")
ORANGE_SOFT = HexColor("#FDF2E9")
ORANGE_BORDER = HexColor("#E59866")
GREEN_SOFT  = HexColor("#EAFAF1")
GREEN_BORDER= HexColor("#52BE80")
RED_SOFT    = HexColor("#FDEDEC")
RED_BORDER  = HexColor("#E74C3C")

PAGE_W, PAGE_H = A4
LEFT_M = RIGHT_M = 2.0 * cm
TOP_M = BOTTOM_M = 2.2 * cm
USABLE_W = PAGE_W - LEFT_M - RIGHT_M

def make_doc(path):
    return SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M,
        topMargin=TOP_M, bottomMargin=BOTTOM_M,
        title="UniMediTrend – Alternative Models & ML Q&A",
        author="GROUP 8, CE 3A – UMaT"
    )

def build_styles():
    S = {}
    S["cover_title"] = ParagraphStyle("cover_title", fontName="Helvetica-Bold", fontSize=24,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=8, leading=30)
    S["cover_sub"] = ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=12,
        textColor=LIGHT_BLUE, alignment=TA_CENTER, spaceAfter=5, leading=17)
    S["cover_meta"] = ParagraphStyle("cover_meta", fontName="Helvetica", fontSize=10,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=4)
    S["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14,
        textColor=WHITE, backColor=ACCENT_BLUE, alignment=TA_LEFT,
        spaceBefore=14, spaceAfter=6, leading=20,
        borderPadding=(6, 10, 6, 10))
    S["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5,
        textColor=ACCENT_BLUE, spaceBefore=10, spaceAfter=4, leading=16)
    S["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10,
        textColor=MID_BLUE, spaceBefore=7, spaceAfter=3, leading=14)
    S["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
        textColor=DARK_TEXT, leading=14.5, spaceAfter=5, alignment=TA_JUSTIFY)
    S["bullet"] = ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.5,
        textColor=DARK_TEXT, leading=14, leftIndent=14, spaceAfter=3)
    S["q"] = ParagraphStyle("q", fontName="Helvetica-Bold", fontSize=10,
        textColor=DARK_NAVY, leading=15, spaceAfter=3, spaceBefore=8,
        backColor=LIGHT_BLUE, borderPadding=(6, 8, 6, 8))
    S["a"] = ParagraphStyle("a", fontName="Helvetica", fontSize=9.5,
        textColor=DARK_TEXT, leading=14.5, spaceAfter=6,
        leftIndent=8, alignment=TA_JUSTIFY)
    S["tag_why"] = ParagraphStyle("tag_why", fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, alignment=TA_CENTER)
    S["callout"] = ParagraphStyle("callout", fontName="Helvetica-Oblique", fontSize=9.5,
        textColor=DARK_NAVY, backColor=LIGHT_BLUE, leading=14,
        spaceAfter=8, spaceBefore=4, leftIndent=8, rightIndent=8,
        borderPadding=(6, 10, 6, 10))
    S["formula"] = ParagraphStyle("formula", fontName="Courier-Bold", fontSize=9,
        textColor=ACCENT_BLUE, alignment=TA_CENTER, backColor=LIGHT_BLUE,
        leading=14, spaceAfter=6, spaceBefore=4, borderPadding=(5, 8, 5, 8))
    S["label"] = ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE)
    S["footer"] = ParagraphStyle("footer", fontName="Helvetica", fontSize=8,
        textColor=BORDER_GRAY, alignment=TA_CENTER)
    S["toc"] = ParagraphStyle("toc", fontName="Helvetica", fontSize=10,
        textColor=DARK_NAVY, leading=16, spaceAfter=2)
    S["section_num"] = ParagraphStyle("section_num", fontName="Helvetica-Bold", fontSize=28,
        textColor=LIGHT_BLUE, alignment=TA_LEFT, leading=32)
    return S

S = build_styles()

def p(text, style="body"):     return Paragraph(text, S[style])
def sp(n=6):                    return Spacer(1, n)
def hr():                       return HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceAfter=8)
def h1(t):                      return p(f"  {t}", "h1")
def h2(t):                      return p(t, "h2")
def h3(t):                      return p(t, "h3")
def body(t):                    return p(t, "body")
def bullet(t):                  return p(f"•  {t}", "bullet")
def callout(t):                 return p(t, "callout")
def formula(t):                 return p(t, "formula")

def Q(num, text):
    return p(f"Q{num}.  {text}", "q")

def A(text):
    return p(text, "a")

def std_table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_BLUE),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 9),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, PALE_GRAY]),
        ("GRID",       (0,0), (-1,-1), 0.5, BORDER_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
    ]))
    return t

def qa_block(num, question, answer_paragraphs):
    """Returns a KeepTogether block for a Q&A pair."""
    items = [Q(num, question), sp(2)]
    for ap in answer_paragraphs:
        items.append(A(ap))
    items.append(sp(4))
    return KeepTogether(items)

# ══════════════════════════════════════════════════════════════════════════
def build_story():
    story = []

    # ── COVER ─────────────────────────────────────────────────────────────
    cover = Table([
        [p("", "cover_title")],
        [p("UniMediTrend", "cover_title")],
        [p("Alternative Models &amp; Deep-Dive ML Q&amp;A", "cover_sub")],
        [p("Why This? Why Not That? — Everything You Need to Defend Your Choices", "cover_sub")],
        [Spacer(1, 20)],
        [HRFlowable(width="55%", thickness=1.5, color=GOLD)],
        [Spacer(1, 20)],
        [p("GROUP 8, CE 3A  |  UMaT, Tarkwa", "cover_meta")],
        [p("Artificial Intelligence in Engineering", "cover_meta")],
        [p("Dr. Abdel-Fatao Hamidu", "cover_meta")],
    ], colWidths=[USABLE_W])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_NAVY),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
    ]))
    story.append(Spacer(1, 2*cm))
    story.append(cover)
    story.append(PageBreak())

    # ── TOC ───────────────────────────────────────────────────────────────
    story.append(h1("Contents"))
    story.append(sp(8))
    for num, title in [
        ("PART A", "Alternative Models We Could Have Used"),
        ("  A1", "Alternative Clustering Models (beyond K-Means)"),
        ("  A2", "Alternative Forecasting / Regression Models (beyond LR & RF)"),
        ("  A3", "Summary Comparison Table — All Models"),
        ("PART B", "Deep-Dive ML Question & Answer Bank"),
        ("  B1", "Why Questions — Defending UniMediTrend Choices"),
        ("  B2", "How / What Questions — Concept Mechanics"),
        ("  B3", "Tricky / Examiner-Favourite Questions"),
    ]:
        story.append(p(f"<b>{num}</b> &nbsp;&nbsp; {title}", "toc"))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PART A — ALTERNATIVE MODELS
    # ══════════════════════════════════════════════════════════════════════
    story.append(h1("PART A — Alternative Models We Could Have Used"))
    story.append(sp(4))
    story.append(body(
        "UniMediTrend used three models: <b>K-Means</b> (clustering), <b>Linear Regression</b> "
        "(forecasting baseline), and <b>Random Forest</b> (forecasting). Below are credible "
        "alternatives for both tasks — what they are, why they could help, and why we didn't use them."
    ))
    story.append(PageBreak())

    # ── A1: ALTERNATIVE CLUSTERING ────────────────────────────────────────
    story.append(h1("A1. Alternative Clustering Models"))
    story.append(sp(6))

    clustering_alts = [
        {
            "name": "DBSCAN",
            "full": "Density-Based Spatial Clustering of Applications with Noise",
            "how": (
                "DBSCAN defines clusters as dense regions of points separated by sparse regions. "
                "It does NOT require you to specify K in advance. It classifies points as: "
                "<b>core points</b> (have at least MinPts neighbours within radius epsilon), "
                "<b>border points</b> (within epsilon of a core point but not core themselves), "
                "and <b>noise/outliers</b> (neither core nor border)."
            ),
            "why_good": [
                "Does not require specifying K — discovers the number of clusters automatically.",
                "Can find clusters of arbitrary shape (not just spherical like K-Means).",
                "Naturally identifies and labels outlier/noise visit records — useful for detecting unusual clinic events.",
                "Better suited if hostel risk profiles form irregular non-spherical groupings.",
            ],
            "why_not": [
                "Requires tuning two hyperparameters: epsilon (neighbourhood radius) and MinPts (minimum points). Choosing these is non-trivial.",
                "Struggles with high-dimensional, one-hot encoded data (the 'curse of dimensionality' makes density estimation unreliable).",
                "Our visit feature space (Model B) is high-dimensional after encoding — DBSCAN would underperform there.",
                "Does not produce a fixed number of interpretable tiers, which is what clinic managers need.",
            ],
        },
        {
            "name": "GMM",
            "full": "Gaussian Mixture Models",
            "how": (
                "GMM assumes data is generated from a mixture of K Gaussian (normal) distributions. "
                "Instead of hard cluster assignment (you belong to cluster 1), GMM gives each point a "
                "<b>probability</b> of belonging to each cluster. It is fit using the "
                "<b>Expectation-Maximization (EM)</b> algorithm."
            ),
            "why_good": [
                "Produces soft/probabilistic cluster assignments — a hostel can be 70% Tier 1, 30% Tier 2. More nuanced than hard K-Means labels.",
                "Allows clusters to have different sizes, shapes, and orientations (elliptical, not just spherical).",
                "Better handles the natural overlap between visit archetypes in Model B.",
                "AIC and BIC criteria can be used to choose the optimal number of components.",
            ],
            "why_not": [
                "More computationally expensive than K-Means — requires iterative EM convergence.",
                "The Gaussian assumption may not hold for clinical data which can be skewed or multimodal.",
                "With only 8 hostels (Model A), fitting a GMM is statistically unreliable — too few data points.",
                "Harder to explain to non-technical stakeholders ('70% probability of being high-risk' vs 'Tier 1 hostel').",
            ],
        },
        {
            "name": "Hierarchical Clustering",
            "full": "Agglomerative / Divisive Hierarchical Clustering",
            "how": (
                "Agglomerative clustering starts with each point as its own cluster, then repeatedly "
                "merges the two closest clusters until one cluster remains. The result is a "
                "<b>dendrogram</b> — a tree diagram showing how clusters merged. You cut the tree "
                "at a chosen height to get your desired number of clusters."
            ),
            "why_good": [
                "Does not require specifying K upfront — you choose the cut level after seeing the dendrogram.",
                "The dendrogram visually shows the natural hierarchy of hostel relationships — which hostels are most similar.",
                "With only 8 hostels (Model A), hierarchical clustering is perfectly sized — K-Means can be unstable with so few points.",
                "No centroid assumption — handles non-spherical cluster shapes.",
            ],
            "why_not": [
                "Computationally expensive for large datasets — O(n^2) memory. Unsuitable for 5,799 individual visit records (Model B).",
                "Once merged, clusters cannot be un-split (agglomerative is greedy — early merge errors propagate).",
                "Dendrogram interpretation requires domain expertise to choose the right cut point.",
            ],
        },
        {
            "name": "K-Medoids (PAM)",
            "full": "Partitioning Around Medoids",
            "how": (
                "Similar to K-Means but instead of using the mean (centroid) of a cluster, "
                "K-Medoids uses actual data points as cluster centres (<b>medoids</b>). "
                "The medoid is the point that minimizes total dissimilarity to all other points in the cluster."
            ),
            "why_good": [
                "More robust to outliers than K-Means — a medoid is a real data point, not a synthetic mean.",
                "Works with any distance metric (not just Euclidean) — useful for mixed-type clinical data.",
                "Actual data points as cluster centres are more interpretable: 'Cluster represented by this specific visit profile'.",
            ],
            "why_not": [
                "Computationally much more expensive than K-Means — O(k * (n-k)^2) per iteration.",
                "For 5,799 records (Model B), PAM would be very slow without approximations.",
                "For our synthetic data with clean Euclidean features, K-Means performs similarly at lower cost.",
            ],
        },
    ]

    for alt in clustering_alts:
        story.append(KeepTogether([
            h2(f"{alt['name']} — {alt['full']}"),
            sp(3),
            body(f"<b>How it works:</b> {alt['how']}"),
            sp(3),
        ]))
        story.append(h3("Why it could have been better for UniMediTrend:"))
        for item in alt["why_good"]:
            story.append(bullet(f"<font color='#1A5276'><b>+</b></font>  {item}"))
        story.append(sp(3))
        story.append(h3("Why we didn't use it / its limitations:"))
        for item in alt["why_not"]:
            story.append(bullet(f"<font color='#922B21'><b>–</b></font>  {item}"))
        story.append(hr())
        story.append(sp(4))

    story.append(PageBreak())

    # ── A2: ALTERNATIVE FORECASTING ───────────────────────────────────────
    story.append(h1("A2. Alternative Forecasting / Regression Models"))
    story.append(sp(6))

    forecast_alts = [
        {
            "name": "XGBoost",
            "full": "Extreme Gradient Boosting",
            "how": (
                "XGBoost is a gradient boosting framework. It builds trees <b>sequentially</b> — "
                "each new tree corrects the errors (residuals) of the previous tree. "
                "It minimizes a regularized loss function using gradient descent. "
                "XGBoost adds L1/L2 regularization, missing value handling, and parallel computation "
                "on top of standard gradient boosting."
            ),
            "why_good": [
                "Handles non-linear relationships between lag features and visit counts much better than Linear Regression.",
                "Built-in regularization (lambda, alpha) prevents overfitting — critical given our small 79-row dataset.",
                "Provides feature importance scores — reveals which lag or cyclical feature drives demand the most.",
                "Consistently outperforms Random Forest on tabular data in practice.",
                "Explicitly mentioned in our Future Work section as a planned improvement.",
            ],
            "why_not": [
                "More hyperparameters to tune (learning rate, max depth, n_estimators, subsample, colsample_bytree) — requires cross-validated tuning.",
                "With only 79 training rows, gradient boosting can still overfit if not carefully regularized.",
                "Less interpretable than Linear Regression — harder to explain coefficient-level reasoning.",
            ],
        },
        {
            "name": "LightGBM",
            "full": "Light Gradient Boosting Machine",
            "how": (
                "LightGBM is Microsoft's gradient boosting framework. It uses two key innovations: "
                "<b>Gradient-Based One-Side Sampling (GOSS)</b> — keeps instances with large gradients "
                "and randomly drops those with small gradients; and <b>Exclusive Feature Bundling (EFB)</b> "
                "— bundles mutually exclusive sparse features to reduce dimensionality. "
                "It grows trees <b>leaf-wise</b> (best-first) rather than level-wise."
            ),
            "why_good": [
                "Faster training than XGBoost — especially relevant if dataset grows larger over time.",
                "Leaf-wise growth captures more complex patterns than level-wise (Random Forest) growth.",
                "Also mentioned in the Future Work section.",
                "Handles categorical features natively without one-hot encoding.",
            ],
            "why_not": [
                "Leaf-wise growth is more prone to overfitting on small datasets — our 79 rows is a significant risk.",
                "Even faster than XGBoost but more complex to tune well.",
            ],
        },
        {
            "name": "ARIMA / SARIMA",
            "full": "AutoRegressive Integrated Moving Average (Seasonal variant)",
            "how": (
                "ARIMA is a classical time-series model. It models the target as a function of: "
                "<b>AR</b> (AutoRegressive) — past values; <b>I</b> (Integrated) — differencing to "
                "make the series stationary; <b>MA</b> (Moving Average) — past forecast errors. "
                "SARIMA adds seasonal components (P, D, Q, s) for periodic patterns."
            ),
            "why_good": [
                "Specifically designed for time-series — handles autocorrelation and trend natively without feature engineering.",
                "SARIMA would directly model the academic semester seasonality we observed in EDA.",
                "Does not require feature engineering of lag, rolling mean, or cyclical encodings — these are built into the model structure.",
                "Well-established statistical framework with interpretable parameters.",
                "Works well on short series (79 rows is reasonable for ARIMA).",
            ],
            "why_not": [
                "Assumes linearity and stationarity — clinic demand driven by non-linear factors (exam stress, disease outbreaks) may violate this.",
                "Requires stationarity testing (ADF test) and careful order selection (p, d, q) — adds complexity.",
                "Pure time-series model — cannot incorporate external features like hostel cluster labels or diagnosis type.",
                "Does not generalize to a machine learning pipeline framework as cleanly as scikit-learn models.",
            ],
        },
        {
            "name": "SVR",
            "full": "Support Vector Regression",
            "how": (
                "SVR applies the Support Vector Machine principle to regression. It tries to fit a "
                "hyperplane within an epsilon-tube around the data, minimizing only errors that fall "
                "outside this tube. The <b>kernel trick</b> (RBF, polynomial, sigmoid) maps data into "
                "higher-dimensional spaces to capture non-linear relationships."
            ),
            "why_good": [
                "Handles non-linear patterns via kernel trick — could capture complex academic cycle effects.",
                "Effective in high-dimensional spaces and small datasets — suitable for our 79-row problem.",
                "Robust to outliers — the epsilon-insensitive loss ignores small errors and focuses on larger deviations.",
            ],
            "why_not": [
                "Requires careful tuning of C (regularization), epsilon (tube width), and kernel parameters.",
                "Not interpretable — no feature importance, no coefficient explanation.",
                "Computationally expensive for large datasets (though irrelevant at 79 rows).",
                "Less naturally suited to time-series than ARIMA or lag-based tree models.",
            ],
        },
        {
            "name": "Ridge / Lasso Regression",
            "full": "Regularized Linear Regression",
            "how": (
                "Ridge (L2) and Lasso (L1) add penalty terms to the Linear Regression loss function "
                "to shrink coefficients. <b>Ridge:</b> adds sum of squared coefficients — shrinks all "
                "coefficients toward zero but rarely to exactly zero. "
                "<b>Lasso:</b> adds sum of absolute coefficients — can shrink some coefficients to "
                "exactly zero, performing automatic <b>feature selection</b>."
            ),
            "why_good": [
                "Our dataset has few rows (79) but several engineered features — regularization prevents overfitting that plain Linear Regression is prone to.",
                "Lasso would automatically identify which lag or cyclical features are most predictive, discarding irrelevant ones.",
                "Ridge would provide a more stable linear baseline than plain OLS when features are correlated (e.g., lag_1 and rolling_mean_4).",
                "Same interpretability as Linear Regression — coefficients are still readable.",
            ],
            "why_not": [
                "Still linear — cannot capture non-linear demand spikes during exam periods or disease outbreaks.",
                "With only 7–10 features, the regularization benefit is modest — overfitting risk is already limited.",
            ],
        },
        {
            "name": "Prophet",
            "full": "Facebook/Meta Prophet",
            "how": (
                "Prophet is a decomposable time-series model developed by Meta. It models the series as: "
                "Trend + Seasonality + Holidays + Noise. It uses a piecewise linear or logistic growth "
                "trend, Fourier series for seasonality, and allows explicit holiday/event effects. "
                "Designed to work well with daily/weekly data with missing values and outliers."
            ),
            "why_good": [
                "Directly models academic semester patterns as seasonality — no need to manually engineer sin/cos encodings.",
                "Handles exam calendar events and public holidays as explicit regressors — exactly the exogenous signals our project lacks.",
                "Robust to missing data and outliers — common in clinic records.",
                "Produces <b>uncertainty intervals</b> — tells the clinic 'we predict 60 visits, but it could range from 45 to 75'.",
                "Very easy to use and interpret for non-technical stakeholders.",
            ],
            "why_not": [
                "Designed for longer time series (ideally 1+ year of daily data) — our 79 weekly points is on the shorter end.",
                "Less flexible for incorporating engineered ML features (cluster labels, diagnosis proportions).",
                "Not part of the scikit-learn ecosystem — harder to integrate into the existing pipeline.",
            ],
        },
    ]

    for alt in forecast_alts:
        story.append(KeepTogether([
            h2(f"{alt['name']} — {alt['full']}"),
            sp(3),
            body(f"<b>How it works:</b> {alt['how']}"),
            sp(3),
        ]))
        story.append(h3("Why it could have improved UniMediTrend's forecasting:"))
        for item in alt["why_good"]:
            story.append(bullet(f"<font color='#1A5276'><b>+</b></font>  {item}"))
        story.append(sp(3))
        story.append(h3("Why we didn't use it / its limitations:"))
        for item in alt["why_not"]:
            story.append(bullet(f"<font color='#922B21'><b>–</b></font>  {item}"))
        story.append(hr())
        story.append(sp(4))

    story.append(PageBreak())

    # ── A3: COMPARISON TABLE ──────────────────────────────────────────────
    story.append(h1("A3. Summary Comparison — All Models"))
    story.append(sp(6))

    story.append(h2("Clustering Models"))
    clust_cmp = [
        [p("Model","label"), p("Needs K?","label"), p("Handles Noise?","label"), p("Shape Assumption","label"), p("Best For","label")],
        [body("K-Means (USED)"), body("Yes"), body("No"), body("Spherical"), body("Known K, clean features, fast")],
        [body("DBSCAN"), body("No"), body("Yes (labels outliers)"), body("Any shape"), body("Irregular clusters, noise detection")],
        [body("GMM"), body("Yes"), body("Soft boundaries"), body("Elliptical"), body("Overlapping clusters, probabilistic assignment")],
        [body("Hierarchical"), body("No (post-hoc)"), body("No"), body("Any shape"), body("Small datasets, dendrogram insight")],
        [body("K-Medoids"), body("Yes"), body("Better than K-Means"), body("Spherical"), body("Outlier robustness, interpretable centres")],
    ]
    story.append(std_table(clust_cmp, col_widths=[USABLE_W*0.22, USABLE_W*0.12, USABLE_W*0.18, USABLE_W*0.18, USABLE_W*0.3]))
    story.append(sp(10))

    story.append(h2("Forecasting Models"))
    fore_cmp = [
        [p("Model","label"), p("Non-Linear?","label"), p("Interpretable?","label"), p("Small Data?","label"), p("Uncertainty?","label"), p("Best For","label")],
        [body("Linear Regression (USED)"), body("No"), body("High"), body("Good"), body("No"), body("Baseline, interpretability")],
        [body("Random Forest (USED)"), body("Yes"), body("Medium"), body("OK"), body("No"), body("Non-linear tabular data")],
        [body("XGBoost"), body("Yes"), body("Medium"), body("Good*"), body("No"), body("Best tabular accuracy")],
        [body("LightGBM"), body("Yes"), body("Medium"), body("Risk"), body("No"), body("Large data, speed")],
        [body("ARIMA/SARIMA"), body("No"), body("High"), body("Good"), body("No"), body("Pure time-series, seasonality")],
        [body("SVR"), body("Yes (kernel)"), body("Low"), body("Good"), body("No"), body("Small high-dim data")],
        [body("Ridge/Lasso"), body("No"), body("High"), body("Good"), body("No"), body("Regularized linear baseline")],
        [body("Prophet"), body("Partial"), body("High"), body("Medium"), body("Yes"), body("Trend+seasonality+events")],
    ]
    story.append(std_table(fore_cmp, col_widths=[USABLE_W*0.22, USABLE_W*0.1, USABLE_W*0.12, USABLE_W*0.1, USABLE_W*0.1, USABLE_W*0.36]))
    story.append(callout("* Good with regularization tuned. Without tuning, XGBoost can overfit on 79 rows."))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # PART B — ML Q&A
    # ══════════════════════════════════════════════════════════════════════
    story.append(h1("PART B — Deep-Dive ML Question & Answer Bank"))
    story.append(sp(4))
    story.append(callout(
        "These are the questions most likely to be asked in a presentation or viva. "
        "Focus especially on the 'Why' questions — these are where marks are won or lost."
    ))
    story.append(PageBreak())

    # ── B1: WHY QUESTIONS ─────────────────────────────────────────────────
    story.append(h1("B1. 'Why' Questions — Defending UniMediTrend Choices"))
    story.append(sp(6))

    why_qas = [
        (
            "Why did you use K-Means and not another clustering algorithm?",
            [
                "K-Means was appropriate for three reasons. First, it is computationally efficient — it scales well to our 5,799 visit records for Model B. Second, we had domain-driven priors: we expected approximately 3 hostel risk tiers and 4 visit archetypes, making specifying K in advance reasonable. Third, our data was preprocessed with StandardScaler and one-hot encoding, producing a relatively clean Euclidean feature space that satisfies K-Means' spherical cluster assumption reasonably well.",
                "The main limitation — that K-Means assumes spherical clusters — is acknowledged. The moderate silhouette score of 0.1120 for Model B confirms some non-spherical overlap, which is why we validated with both the Elbow Method and Silhouette analysis rather than relying on K-Means output blindly.",
            ]
        ),
        (
            "Why did you choose K=3 for Model A and K=4 for Model B?",
            [
                "For Model A (hostel risk), K=3 was chosen using both quantitative and qualitative reasoning. The Elbow Method showed diminishing inertia returns beyond K=3 for the hostel-level profile matrix. The Silhouette Score of 0.3772 at K=3 was the highest across tested values. Qualitatively, K=3 maps naturally onto three operationally meaningful intervention categories: malaria control, stress/mental health, and sanitation/food safety.",
                "For Model B (visit archetypes), K=4 was chosen from the Elbow and Silhouette diagnostics shown in Figure 6.1. K=4 also aligns with clinically interpretable categories — tropical illness, waterborne/severe, burnout, and minor ailments — which makes the output actionable for clinic staff.",
            ]
        ),
        (
            "Why did you use a synthetic dataset instead of real clinic data?",
            [
                "Health records contain sensitive personal data (name, diagnosis, residential location) which is subject to strict data protection regulations. Using real data without formal ethical clearance and anonymization protocols would be a governance violation.",
                "Synthetic data was generated to preserve statistical complexity — including realistic academic cycles, seasonal disease patterns, and diagnosis distributions — while ensuring no real patient is identifiable. This is a standard approach in healthcare AI research and protects both patients and the research team.",
            ]
        ),
        (
            "Why did you use StandardScaler before running K-Means?",
            [
                "K-Means assigns points to clusters based on Euclidean distance to centroids. If features are on different scales — for example, severity ranges from 1–10 while a one-hot encoded hostel column is 0 or 1 — the larger-valued features will dominate the distance calculation, making the clustering effectively ignore the smaller-valued features.",
                "StandardScaler transforms each feature to have mean=0 and standard deviation=1, putting all features on equal footing. Without scaling, K-Means would produce clusters driven almost entirely by the highest-variance features, regardless of their clinical importance.",
            ]
        ),
        (
            "Why did you use one-hot encoding instead of label encoding?",
            [
                "Label encoding assigns arbitrary integers to categories (e.g., Malaria=1, Typhoid=2, Cold=3). This implies an ordinal relationship — that Typhoid is 'more' than Malaria — which is clinically meaningless and would mislead both K-Means (which uses distance) and linear regression (which assumes numeric relationships).",
                "One-hot encoding creates a separate binary column for each category, treating all diagnoses as equally distinct with no implied ordering. For distance-based algorithms and linear models, one-hot encoding is the correct approach for nominal categorical variables.",
            ]
        ),
        (
            "Why did you use a chronological holdout split instead of random split?",
            [
                "Our target variable is weekly visit counts — a time-ordered sequence. Random splitting would allow the model to train on future data and test on past data, which constitutes look-ahead leakage. The model would appear to perform well because it has already 'seen' future patterns during training.",
                "In real deployment, we only ever know the past. A chronological 80/20 split correctly simulates this: the model trains on weeks 1 through 63 and is tested on weeks 64 through 79 — data it has genuinely never seen. This gives an honest estimate of real-world predictive performance.",
            ]
        ),
        (
            "Why did you use 5-Fold TimeSeriesSplit instead of standard k-fold cross-validation?",
            [
                "Standard k-fold cross-validation randomly shuffles data before splitting. For time-series data, this is invalid — it breaks the temporal ordering and allows future information to contaminate training folds, producing optimistically biased performance estimates.",
                "TimeSeriesSplit uses expanding training windows: Fold 1 trains on the first 20% and tests on the next 20%; Fold 2 trains on the first 40% and tests on the next 20%; and so on. This correctly simulates how the model would be used in practice — always predicting forward in time — while also giving us robustness diagnostics across multiple academic sub-periods.",
            ]
        ),
        (
            "Why were your R² values negative, and does that mean the project failed?",
            [
                "Negative R² means the model's predictions were worse than simply predicting the historical mean for every week. For example, if average weekly visits is 65 and we just predicted 65 every week, that naive baseline would have scored R²=0. Our models scored R²=-0.18 and -0.50, meaning they made the prediction worse in those specific experimental conditions.",
                "This is NOT a project failure — it is a diagnostic finding. The pipeline is correctly engineered: data is clean, features are sound, validation is rigorous. What is missing are exogenous signals. Clinic demand is driven by factors outside the visit records themselves — exam timetables, weather, disease outbreaks. Without these, the model has insufficient information to beat a simple mean. The report is transparent about this limitation, which is itself a mark of scientific integrity.",
            ]
        ),
        (
            "Why did you use PCA only for visualization and not as a preprocessing step for clustering?",
            [
                "PCA reduces dimensionality by projecting data onto lower-dimensional principal components. If used before clustering, it would change the feature space that K-Means operates on, which could lose clinically meaningful variance in specific diagnosis columns.",
                "We used PCA only as a post-hoc visualization tool — to project the K=4 cluster results into 2D (PC1 vs PC2) for Figure 6.2. The actual K-Means assignment was done in the full original feature space. This preserves the integrity of the clustering while still allowing us to visually inspect and communicate cluster separation.",
            ]
        ),
        (
            "Why did you use lag features instead of just using the raw time index as a feature?",
            [
                "The raw time index (week number 1, 2, 3...) tells the model nothing about the recent clinical context — it only encodes 'how far along in time we are'. It cannot capture the fact that a spike last week often predicts higher demand this week.",
                "Lag features (lag_1, lag_2, lag_3) give the model short-term memory of actual visit volumes. If last week had 100 visits, the model learns this likely precedes a continued high-demand period. If last week had 5 visits (semester break), the model learns demand is likely still low. This is a form of autoregressive modeling — encoding the signal's own recent history as predictive information.",
            ]
        ),
        (
            "Why did you use rolling_mean_4 as a feature?",
            [
                "Individual weekly visit counts are noisy — a single week might spike due to a food poisoning event that resolves the following week. A single lag feature would then train the model to expect continued high visits when the spike was in fact temporary.",
                "The 4-week rolling mean smooths out these short-term fluctuations and gives the model a view of the prevailing demand trend rather than instantaneous noise. It captures whether the general trend is upward, downward, or stable — a cleaner signal for predicting the next week's baseline demand.",
            ]
        ),
    ]

    for i, (q, ans) in enumerate(why_qas, 1):
        story.append(qa_block(i, q, ans))

    story.append(PageBreak())

    # ── B2: HOW/WHAT QUESTIONS ────────────────────────────────────────────
    story.append(h1("B2. 'How / What' Questions — Concept Mechanics"))
    story.append(sp(6))

    how_qas = [
        (
            "What is the difference between supervised and unsupervised learning? Give examples from UniMediTrend.",
            [
                "In supervised learning, the model is trained on labelled examples — pairs of (input, correct output). The model learns to map inputs to outputs by minimizing prediction error. In UniMediTrend, forecasting is supervised: the input is a feature vector (lag_1, rolling_mean_4, month_sin...) and the label is the known total_visits for that week. The model learns the mapping.",
                "In unsupervised learning, there are no labels — the model must discover structure in the data entirely on its own. In UniMediTrend, clustering is unsupervised: we give K-Means the hostel profile matrix or visit feature vectors with no pre-assigned risk tiers. K-Means discovers the tiers by finding natural groupings based on similarity.",
            ]
        ),
        (
            "What is the Elbow Method and how does it work mathematically?",
            [
                "The Elbow Method plots inertia against increasing values of K (typically K=2 to K=10). Inertia is the within-cluster sum of squared distances: for every point, compute its squared Euclidean distance to its assigned centroid, then sum all these values across all clusters. As K increases, inertia always decreases — at K=N (each point is its own cluster), inertia is zero.",
                "The 'elbow' is the point where the rate of inertia decrease changes from steep to shallow — where adding another cluster provides diminishing marginal improvement in compactness. This is chosen as the optimal K. For Model B, the elbow was observed at K=4, supporting our choice.",
            ]
        ),
        (
            "What is the difference between MAE and RMSE? When would you prefer one over the other?",
            [
                "MAE (Mean Absolute Error) is the average of absolute differences between actual and predicted values. Every error contributes equally regardless of its size. RMSE (Root Mean Squared Error) squares errors before averaging, then takes the square root — this means large errors are penalized disproportionately more than small ones.",
                "You prefer MAE when outliers should not dominate the evaluation — for example, if a single exceptional disease outbreak week is not representative of normal operations. You prefer RMSE when large prediction errors are especially costly — for example, if a severe underestimate by 40 visits is much worse than two underestimates by 20 visits each. For clinic planning, RMSE is arguably more relevant because a severe stockout from one very wrong prediction could be dangerous.",
            ]
        ),
        (
            "What is Random Forest and why does it outperform a single Decision Tree?",
            [
                "A Decision Tree splits data based on feature thresholds to minimize a loss criterion (e.g., MSE for regression). A single tree is highly prone to overfitting — it memorizes the training data structure including noise. If trained on slightly different data, it produces very different splits (high variance).",
                "Random Forest addresses this by training many trees (the forest), where each tree is trained on a bootstrap sample of the data AND only considers a random subset of features at each split. The final prediction is the average across all trees. Because each tree makes different errors (due to randomness), averaging cancels out individual errors — this is called variance reduction through ensembling. The result is a model that generalizes far better than any individual tree.",
            ]
        ),
        (
            "What is cross-validation and why is regular k-fold invalid for time-series data?",
            [
                "Cross-validation repeatedly splits data into train and test sets to get a more reliable performance estimate than a single split. Standard k-fold shuffles the data randomly and creates k equally sized folds, training on k-1 and testing on the remaining 1, cycling through all folds.",
                "For time-series data, this is invalid because shuffling destroys temporal ordering. If Fold 3 (which temporally occurs in month 6) is used for training and Fold 1 (month 2) for testing, the model is trained on the future to predict the past — look-ahead leakage. TimeSeriesSplit prevents this by always training on the past and testing on the future, respecting the arrow of time.",
            ]
        ),
        (
            "What does it mean for K-Means to 'converge', and is convergence guaranteed?",
            [
                "K-Means converges when no data point changes its cluster assignment from one iteration to the next — the centroids stop moving. At this point, further iterations produce identical results, so the algorithm stops.",
                "Convergence to some solution is guaranteed — K-Means will always terminate. However, it is NOT guaranteed to converge to the global optimum. Because initial centroid positions are random, K-Means can converge to a local minimum where clusters are suboptimal. This is why K-Means is typically run multiple times with different random initializations (controlled by random_state=42 in scikit-learn) and the best result (lowest inertia) is kept.",
            ]
        ),
        (
            "What is feature engineering, and why was it necessary for the forecasting model?",
            [
                "Feature engineering is the process of creating new input variables from raw data that better capture the patterns the model needs to learn. Raw data alone (a date column and a visit count) cannot be directly fed into a regression model in a way that captures temporal structure.",
                "For UniMediTrend, feature engineering created: lag features (converting the temporal sequence into usable numeric inputs), a rolling mean (capturing trend signal), and cyclical encodings (converting month/week into a continuous representation that correctly handles year-end wrap-around). Without these engineered features, the regression model would have almost no useful signal — it would essentially be predicting visit counts from just a date number, which carries no inherent demand information.",
            ]
        ),
        (
            "What is the difference between a model parameter and a hyperparameter?",
            [
                "A model parameter is a value learned automatically from data during training. Examples: the regression coefficients (beta values) in Linear Regression, the centroid positions in K-Means, and the tree split thresholds in Random Forest. You never set these manually — the algorithm finds optimal values.",
                "A hyperparameter is a setting that controls the learning process itself, set by the user before training begins. Examples: K (number of clusters in K-Means), the number of trees in Random Forest (n_estimators), the learning rate in XGBoost, and the regularization strength in Ridge Regression. Hyperparameters are chosen via techniques like grid search or cross-validation, not learned from the training data directly.",
            ]
        ),
    ]

    for i, (q, ans) in enumerate(how_qas, 1):
        story.append(qa_block(i, q, ans))

    story.append(PageBreak())

    # ── B3: TRICKY QUESTIONS ──────────────────────────────────────────────
    story.append(h1("B3. Tricky / Examiner-Favourite Questions"))
    story.append(sp(6))

    tricky_qas = [
        (
            "Random Forest is more powerful than Linear Regression. Why did Linear Regression perform BETTER on your holdout set?",
            [
                "Our dataset had only 79 weekly rows after aggregation. Random Forest, despite its ensemble design, is a high-variance model — it needs sufficient training data to generalize well. With so few rows, Random Forest overfit to the training data's specific noise patterns and failed to generalize to the holdout set.",
                "Linear Regression has lower variance — it produces a simpler, smoother fit that is less sensitive to individual data points. On a small, noisy 79-row dataset, this simplicity was actually an advantage. This phenomenon is called the bias-variance tradeoff: in low-data regimes, higher-bias, lower-variance models often win. Random Forest would be expected to dominate with thousands of training rows.",
            ]
        ),
        (
            "If your R² is negative, why not just use the mean as your prediction? Isn't that provably better?",
            [
                "This is an excellent critical question. On the specific holdout test set in this experiment, yes — predicting the historical mean every week would have scored R²=0, outperforming our models. However, this does not mean the mean is a useful predictor in practice.",
                "Predicting the mean gives clinic managers no actionable information — it says 'expect the same as always' regardless of whether exams are approaching, a disease outbreak is occurring, or it is semester break. Our models, despite poor R², at least attempt to incorporate recent trends via lag features and seasonal patterns. The appropriate next step is to add exogenous signals (exam calendar, weather) — not to abandon ML in favour of a naive constant. The negative R² is a diagnostic that the current feature set is insufficient, not that the approach is wrong.",
            ]
        ),
        (
            "Could you have used a neural network for this project? Why or why not?",
            [
                "Technically yes — a recurrent neural network (RNN) or Long Short-Term Memory (LSTM) network is specifically designed for sequential time-series data and could capture complex temporal dependencies that lag features approximate more crudely.",
                "However, a neural network would be a poor choice for UniMediTrend for three reasons. First, we only have 79 training rows — neural networks are notoriously data-hungry and would massively overfit. Second, neural networks are opaque black boxes with no interpretability — for a healthcare planning tool where decisions affect staffing and medicine procurement, explainability to clinic management is critical. Third, the deployment complexity of a neural network is significantly higher than a serialized sklearn model. The project's goal was a deployable, auditable pipeline — neural networks are disproportionate to that goal at this scale.",
            ]
        ),
        (
            "Why is the silhouette score for Model B (0.1120) so much lower than Model A (0.3772)?",
            [
                "Model A clusters at the hostel level — 8 hostels described by aggregated diagnosis proportions. Aggregation smooths out individual visit noise, producing cleaner, more separable hostel profiles. The signal-to-noise ratio is higher when you are comparing 8 summarized profiles.",
                "Model B clusters at the individual visit level — 5,799 records described by one-hot encoded diagnosis, severity, hostel, level, gender, and department. Individual visits are inherently noisier. A real student can have malaria AND stress-induced fatigue simultaneously, placing their visit profile on the boundary between Cluster 0 and Cluster 2. This genuine clinical overlap produces lower silhouette scores. It is a reflection of reality, not a modelling failure — the report correctly notes that moderate overlap 'indicates mixed-case real-world visit behaviour rather than perfectly separable categories'.",
            ]
        ),
        (
            "What would you change about the project if you had more time and real data?",
            [
                "With real data, the first priority would be integrating exogenous signals: the academic calendar (exam dates, semester start/end), weather data (rainfall and humidity correlate with malaria and waterborne illness incidence), and public health event records. These are the missing predictors that likely explain the negative R².",
                "On the modelling side, we would replace Random Forest with XGBoost or LightGBM — both mentioned in Future Work — with proper cross-validated hyperparameter tuning. We would add probabilistic forecasting (prediction intervals) using quantile regression or conformal prediction, giving the clinic a confidence range rather than a single point estimate. For clustering, we would test GMM to get soft probabilistic hostel assignments. Finally, we would implement drift monitoring — alerting when real incoming data diverges significantly from the training distribution, triggering a model retrain.",
            ]
        ),
        (
            "What is the curse of dimensionality and how did it affect your project?",
            [
                "The curse of dimensionality refers to the phenomenon where, as the number of dimensions (features) in a dataset increases, the data becomes increasingly sparse. In high-dimensional spaces, all points tend to become equidistant from each other — making distance-based metrics like Euclidean distance less meaningful.",
                "In UniMediTrend, Model B applies K-Means to a one-hot encoded visit feature space with many columns (multiple diagnosis categories, multiple hostels, multiple departments). This high dimensionality partially explains the low silhouette score of 0.1120 — in high-dimensional space, K-Means struggles to find well-separated clusters because the concept of 'distance' degrades. This is one reason DBSCAN would also struggle in our Model B space — its density estimation is similarly affected. PCA could have been applied as a preprocessing step to reduce dimensions before clustering, which might have improved separation.",
            ]
        ),
        (
            "Why is idempotency important in your MongoDB pipeline design?",
            [
                "Idempotency means running the same pipeline operation multiple times produces the same result — no duplicate records, no cascading errors. In a data engineering pipeline that may be rerun during development, debugging, or scheduled refreshes, non-idempotent operations can corrupt data.",
                "For example, if the enrichment pipeline inserts cluster labels into the database without first checking for existing records, each re-run would add duplicate enriched documents. The Raw vs Enriched collection separation ensures the raw data is never modified (immutable baseline), and the enrichment process can safely overwrite or upsert enriched records on each run. This design is critical for reproducibility — a core principle of auditable AI systems.",
            ]
        ),
    ]

    for i, (q, ans) in enumerate(tricky_qas, 1):
        story.append(qa_block(i, q, ans))

    # ── FOOTER ────────────────────────────────────────────────────────────
    story.append(hr())
    story.append(p(
        "UniMediTrend — Alternative Models &amp; ML Q&amp;A  |  GROUP 8, CE 3A  |  UMaT, Tarkwa",
        "footer"
    ))

    return story

# ── BUILD ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out = "UniMediTrend_Models_QA.pdf"
    doc = make_doc(out)
    story = build_story()
    doc.build(story)
    print(f"Done: {out}")