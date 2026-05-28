# UniMediTrend Submission Checklist

## A. Hard Copy (Printed Report)
1. Print PROJECT_REPORT.md content as a formatted report (or convert to PDF first, then print).
2. Ensure cover page includes:
   - Project title
   - Group members and index numbers
   - Course code/title
   - Department and institution
   - Submission date
3. Ensure pages are numbered and stapled/bound.
4. Include key figures from:
   - actual_vs_predicted.png
   - feature_importance.png
   - model_comparison.png
   - tier_breakdown_forecast.png
5. Attach references/appendix section showing notebook and code sources.

## B. Soft Copy (Digital Package)
Include all of these in one folder before zipping:
1. Notebooks:
   - 01_Data_Generation_and_DB_Setup.ipynb
   - 02_EDA_and_Visualisation.ipynb
   - 03_KMeans_Clustering.ipynb
   - 04_Supervised_Learning.ipynb
2. Report files:
   - PROJECT_REPORT.md
   - SUBMISSION_CHECKLIST.md
3. Source code:
   - app.py
   - generate_dataset.py
4. Dependency file:
   - requirements.txt
5. Data files:
   - umat_health_records.csv
   - UniMediTrend – UMaT Student Health Visit Record (Responses) - Form Responses 1 (1).csv
   - snapshots/ (entire folder)
6. Output visuals:
   - actual_vs_predicted.png
   - feature_importance.png
   - model_comparison.png
   - tier_breakdown_forecast.png
7. Optional branding asset:
   - umatlogo.png

## C. Zip Packaging (Windows)
From the project parent directory, run:

```powershell
Compress-Archive -Path .\UniMedi-Trend\* -DestinationPath .\UniMedi-Trend_Submission.zip -Force
```

Or right-click folder -> Send to -> Compressed (zipped) folder.

## D. Final Verification Before Submission
1. Open the zip and confirm all notebooks are present.
2. Open 04_Supervised_Learning.ipynb and verify training code cells are visible.
3. Confirm report file opens correctly.
4. Confirm figures are viewable.
5. Confirm no missing dependency file (requirements.txt).
6. Confirm group member details are inserted on the title page.

## E. Recommended Naming Convention
- Hard copy title page: UniMediTrend AI-Based Analysis and Prediction of Student Clinic Visits
- Soft copy zip: UniMediTrend_GroupX_Submission.zip
