# Post-Project Analysis:

## Project Focus and Purpose

Through a geographical and contextual analysis of internally displaced people (IDPs), food insecurity, medical needs, health facility functionality, market functionality, and regional access constraints, this project examines the ongoing humanitarian crisis in Tigray. Using sub-regional mapping in conjunction with post-conflict reports, the analysis aims to convey how these indicators interact geographically and how they reflect broader patterns of civilian harm, livelihood collapse, and systemic destabilization within Tigray.

The objective of the analysis was not only to visualize humanitarian need but also to interpret how displacement, collapse of basic services, and agricultural destruction operate together as mutually reinforcing mechanisms. The maps were designed to show where stress is concentrated, while the written analysis explains why these patterns exist and how they affect the civilian population over time.

---

## Methodology and Analytical Approach

Geographical analysis was conducted in QGIS using zone-level administrative boundaries. Prior to mapping, datasets were processed in Python using pandas to rank regions according to severity across food and medical needs and access constraints, structure region-level indicators, check for missing values, and create derived metrics (such as displacement rate per population).

Python has also been utilized to create summary tables and bar-chart visualizations in order to verify patterns prior to geographical joins. The cleaned and organized results were combined in QGIS using standardized region and zone IDs. Relative intensity was visualized using graduated symbology rather than a single value.

---

### AI Statement

AI tools were utilized for language refinement, structural guidance, and writing feedback. All data analysis, source selection, interpretation, and conclusions were conducted independently by the analyst.

---

## II. Internally Displaced Persons (IDPs): Scale, Distribution, and Impact

According to humanitarian reports, after the conflict started, displacement in Tigray reached previously unprecedented levels. In response to the ongoing conflict, there were an estimated 1.9 million internally displaced people in Tigray by May 2021; by the end of 2021, that number had doubled to an estimated 4.2 million (GEOGLAM Crop Monitor – Conflict and Food Insecurity Report, 2022).

These figures show both the severity and the geographically restricted nature of displacement because the majority of population movement occurred within Tigray rather than across borders. Zone-level mapping shows that the western and central zones have higher displacement concentrations. 

---

## References and Data Sources

### Analytical Framing and Methodology
The analytical approach and framing for this project were developed by the analyst, informed by common geographical analysis practices and widely applied humanitarian data standards. Rather than relying on a single source to define the project design, the framework was built through an integrated analytical approach that examines geographical relationships and interprets multiple data points together.

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
The synthesis presented in this project is the analyst’s interpretation understood by the geographical overlap of multiple humanitarian data sets. Patterns and trends were identified by examining the overlap between displacement, agricultural collapse, market disruption, and health system failure using mapped HDX datasets alongside GEOGLAM Crop Monitor reporting.

---

### Limitations and Ethical Considerations
Statements addressing data gaps, access constraints, and ethical visualization choices reflect the analyst’s methodical judgment and understanding of compliance to standard practices in conflict-zone and humanitarian geographical analysis. As these considerations are procedural and ethical in nature, no direct external citations were presented.
