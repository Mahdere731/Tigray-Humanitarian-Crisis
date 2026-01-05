# Post-Project Analysis: Systematic Destabilization of Tigray Through Violent Displacement and Agricultural Destruction

## Project Focus and Purpose

Through a spatial and contextual analysis of internally displaced people (IDPs), food insecurity, medical needs, health facility functionality, market functionality, and regional access constraints, this project examines the ongoing humanitarian crisis in Tigray. Using sub-regional mapping in conjunction with post-conflict reports, the analysis aims to convey how these indicators interact spatially and how they reflect broader patterns of civilian harm, livelihood collapse, and systemic destabilization within Tigray.

The objective of the analysis was not only to visualize humanitarian need but also to interpret how displacement, collapse of basic services, and agricultural destruction operate together as mutually reinforcing mechanisms. The maps were designed to show where stress is concentrated, while the written analysis explains why these patterns exist and how they affect the civilian population over time.

---

## Methodology and Analytical Approach

Spatial analysis was conducted in QGIS using zone-level administrative boundaries. Prior to mapping, datasets were processed in Python using pandas to rank regions according to severity across food and medical needs and access constraints, structure region-level indicators, check for missing values, and create derived metrics (such as displacement rate per population).

Python was also used to generate summary tables and bar-chart visualizations to validate patterns prior to spatial joins. Cleaned and organized outputs were then merged in QGIS using standardized region and zone identifiers. Graduated symbology was applied to visualize relative intensity rather than absolute precision.

### AI Statement

AI tools were utilized for language refinement, structural guidance, and writing feedback. All data analysis, source selection, interpretation, and conclusions were conducted independently by the analyst.

---

## II. Internally Displaced Persons (IDPs): Scale, Distribution, and Impact

Humanitarian reporting indicates that displacement in Tigray reached unprecedented levels following the outbreak of conflict. By May 2021, the number of internally displaced persons in Tigray had reached approximately 1.9 million, and by the end of 2021, displacement had doubled to an estimated 4.2 million people due to the ongoing conflict (GEOGLAM Crop Monitor – Conflict and Food Insecurity Report, 2022).

These figures reflect both the severity and the geographically constrained nature of displacement, as population movement largely occurred within Tigray rather than across borders. Zone-level mapping illustrates higher concentrations of displacement in western and central zones. 

---

## References and Data Sources

### Analytical Framing and Methodology
- Methodological overview and analytical framing developed by the author based on spatial analysis practices and humanitarian data standards.
- No single external source cited for project design.

---

### Internally Displaced Persons (IDPs)
- GEOGLAM Crop Monitor – Conflict and Food Insecurity Reports (2021–2022).  
  https://www.cropmonitor.org/conflict-reports

- Humanitarian Data Exchange (HDX) – Ethiopia Internal Displacement (IOM / DTM).  
  https://data.humdata.org/group/eth

- HDX – Ethiopia IDP Subnational Datasets (zone-level).  
  https://data.humdata.org/search?q=ethiopia+idp

---

### Agricultural Sector Destabilization (Tigray)
- GEOGLAM Crop Monitor – Ethiopia and Tigray Context Sections.  
  https://www.cropmonitor.org/conflict-reports

- GEOGLAM Crop Monitor – Documentation of crop destruction, field abandonment, prevention of ploughing and harvesting, seed system disruption, and livestock loss.  
  https://www.cropmonitor.org/conflict-reports

Interpretive synthesis in this section is grounded in repeated mechanisms documented across multiple Crop Monitor reports.

---

### Functional Markets and Economic Strain
- HDX – Functional Markets and Market Functionality Datasets (Ethiopia).  
  https://data.humdata.org/search?q=functional+markets+ethiopia

- GEOGLAM Crop Monitor – Market access, food affordability, and displacement-related market strain.  
  https://www.cropmonitor.org/conflict-reports

---

### Health System Disruption and Medical Need
- HDX – Health Facilities Operational Status (Ethiopia / Tigray).  
  https://data.humdata.org/search?q=health+facilities+ethiopia

- HDX – Medical Need and Humanitarian Needs Overview Datasets.  
  https://data.humdata.org/search?q=medical+need+ethiopia

- GEOGLAM Crop Monitor – Nutrition impacts and food insecurity-related health outcomes.  
  https://www.cropmonitor.org/conflict-reports

- HDX – Access Severity and Regional Access Constraint Datasets.  
  https://data.humdata.org/search?q=access+constraints+ethiopia

---

### Systematic Destabilization (Synthesis)
- Analytical synthesis based on spatial convergence of HDX humanitarian indicators and GEOGLAM Crop Monitor reporting.
- Interpretation reflects multi-layer interaction between displacement, agricultural collapse, market disruption, and health system failure.

---

### Limitations and Ethical Considerations
- Methodological statements regarding data gaps, access constraints, and ethical visualization choices are based on standard practices for conflict-zone analysis.
- No direct external citations required for these sections.

