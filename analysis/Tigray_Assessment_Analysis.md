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
The methodological approach and analytical framing for this project were developed by the author, drawing on established spatial analysis practices and commonly used humanitarian data standards. No single external source was used to define the overall project design; instead, the framework reflects an integrated analytical approach based on spatial correlation and multi-indicator interpretation.

---

### Internally Displaced Persons (IDPs)
Data and contextual information on internal displacement were drawn from the following sources:

- GEOGLAM Crop Monitor – Conflict and Food Insecurity Reports (2021–2022)  
  https://www.cropmonitor.org/conflict-reports

- Humanitarian Data Exchange (HDX) – Ethiopia Internal Displacement datasets (IOM / DTM)  
  https://data.humdata.org/group/eth

- HDX – Ethiopia IDP Subnational (zone-level) datasets  
  https://data.humdata.org/search?q=ethiopia+idp

---

### Agricultural Sector Destabilization (Tigray)
Analysis of agricultural disruption in Tigray was informed primarily by GEOGLAM Crop Monitor reporting, including regional context sections and detailed documentation of conflict-related impacts on agricultural systems.

- GEOGLAM Crop Monitor – Ethiopia and Tigray context sections  
  https://www.cropmonitor.org/conflict-reports

- GEOGLAM Crop Monitor – Documentation of crop destruction, field abandonment, prevention of ploughing and harvesting, disruption of seed systems, and livestock loss  
  https://www.cropmonitor.org/conflict-reports

Interpretive synthesis in this section reflects the author’s analysis of recurring mechanisms documented across multiple Crop Monitor reports rather than reliance on a single incident or data point.

---

### Functional Markets and Economic Strain
Market functionality and economic strain were examined using humanitarian market datasets in combination with contextual reporting on food access and displacement-related pressures.

- HDX – Functional Markets and Market Functionality datasets (Ethiopia)  
  https://data.humdata.org/search?q=functional+markets+ethiopia

- GEOGLAM Crop Monitor – Analysis of market access, food affordability, and displacement-driven market strain  
  https://www.cropmonitor.org/conflict-reports

---

### Health System Disruption and Medical Need
Information on health system functionality and medical need was sourced from humanitarian datasets and conflict impact reporting.

- HDX – Health Facilities Operational Status datasets (Ethiopia / Tigray)  
  https://data.humdata.org/search?q=health+facilities+ethiopia

- HDX – Medical Need and Humanitarian Needs Overview datasets  
  https://data.humdata.org/search?q=medical+need+ethiopia

- GEOGLAM Crop Monitor – Reporting on nutrition impacts and food insecurity-related health outcomes  
  https://www.cropmonitor.org/conflict-reports

- HDX – Access Severity and Regional Access Constraint datasets  
  https://data.humdata.org/search?q=access+constraints+ethiopia

---

### Systematic Destabilization (Synthesis)
The synthesis presented in this project is the author’s interpretation based on the spatial convergence of multiple humanitarian indicators. Patterns were identified by examining the overlap between displacement, agricultural collapse, market disruption, and health system failure using mapped HDX datasets alongside GEOGLAM Crop Monitor reporting.

---

### Limitations and Ethical Considerations
Statements regarding data gaps, access constraints, and ethical visualization choices reflect the author’s methodological judgment and adherence to standard practices in conflict-zone and humanitarian spatial analysis. No direct external citations were required for these methodological and ethical considerations.
