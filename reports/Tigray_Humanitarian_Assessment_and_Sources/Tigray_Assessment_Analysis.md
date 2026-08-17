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

## Sources Cited: Datasets, Assessments, and Reports

### Analytical Framing and Methodology

The analytical approach and framing for this project were developed by the analyst, informed by common geographical analysis practices and widely applied humanitarian data standards. Rather than relying on a single source to define the project design, the framework was built through an integrated analytical approach that examines geographical relationships and interprets multiple data points together.

---

### Internally Displaced Persons (IDPs)

- GEOGLAM Crop Monitor – Conflict and Food Insecurity Reports (2021–2022)  
  https://www.cropmonitor.org/conflict-reports

- Humanitarian Data Exchange (HDX) – Ethiopia Internal Displacement datasets (IOM / DTM)  
  https://data.humdata.org/group/eth

- HDX – Ethiopia IDP Subnational (zone-level) datasets  
  https://data.humdata.org/search?q=ethiopia+idp

---

### Agricultural Sector Destabilization (Tigray)

- GEOGLAM Crop Monitor – Ethiopia and Tigray context sections  
  https://www.cropmonitor.org/conflict-reports

- GEOGLAM Crop Monitor – Documentation of crop destruction, field abandonment, prevention of ploughing and harvesting, disruption of seed systems, and livestock loss  
  https://www.cropmonitor.org/conflict-reports

---

### Functional Markets and Economic Strain

- HDX – Functional Markets and Market Functionality datasets (Ethiopia)  
  https://data.humdata.org/search?q=functional+markets+ethiopia

- GEOGLAM Crop Monitor – Analysis of market access, food affordability, and displacement-driven market strain  
  https://www.cropmonitor.org/conflict-reports

---

### Health System Disruption and Medical Need

- HDX – Health Facilities Operational Status datasets (Ethiopia / Tigray)  
  https://data.humdata.org/search?q=health+facilities+ethiopia

- HDX – Medical Need and Humanitarian Needs Overview datasets  
  https://data.humdata.org/search?q=medical+need+ethiopia

- GEOGLAM Crop Monitor – Reporting on nutrition impacts and food insecurity-related health outcomes  
  https://www.cropmonitor.org/conflict-reports

- HDX – Access Severity and Regional Access Constraint datasets (OCHA / REACH)  
  https://data.humdata.org/search?q=access+constraints+ethiopia

- Gufue et al. (2024) – Academic study analyzing conflict-related damage to the public health system in Tigray  
  https://doi.org/10.3389/fpubh.2024.1271028

- UNICEF & Tigray Regional Health Bureau – Health Facility Damage Assessments (2021–2022)  
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11026641/

- UNOCHA – Ethiopia Humanitarian Needs Overview (2024)  
  https://www.unocha.org/publications/report/ethiopia/ethiopia-humanitarian-needs-overview-2024-february-2024

---

### Source for Killings of Aid Workers & United Nations Guards

- MSF – Assessment of Internal Review into the Killing of Three MSF Staff in Tigray (2021)  
  https://www.msf.org/msf-releases-findings-internal-review-2021-killing-staff-tigray

- Relief Web - Statement on the killing of 23 aid workers in the Tigray region since the start of the crisis
  https://reliefweb.int/report/ethiopia/hc-ai-statement-killing-23-aid-workers-tigray-region-start-crisis

---

### Human Rights and Atrocity Documentation

- Human Rights Watch – _Crimes Against Humanity in Western Tigray Zone_ (2022)  
  https://www.hrw.org/news/2022/04/06/ethiopia-crimes-against-humanity-western-tigray-zone

- Human Rights Watch – _Ethnic Cleansing Persists Under Tigray Truce_ (2023)  
  https://www.hrw.org/news/2023/06/01/ethiopia-ethnic-cleansing-persists-under-tigray-truce

- Amnesty International – _Crimes Against Humanity in Western Tigray Zone_ (2022)  
  https://www.amnesty.org/en/latest/news/2022/04/ethiopia-crimes-against-humanity-in-western-tigray-zone

---

### Systematic Destabilization (Synthesis)

The synthesis displayed in this project is the analyst's interpretation understood by the geographical overlap of multiple humanitarian datasets, and corroborated reports. Patterns and trends were identified by examining the connection between displacement, agricultural collapse, market disruption, and health system failure using identified HDX datasets alongside GEOGLAM Crop Monitor reporting, UNOCHA Humanitarian Needs Overview, UNICEF and Tigray Health Bureau assessments, and human rights documentation from Human Rights Watch as well as Amnesty International.

---

### Limitations and Ethical Considerations

Statements addressing data gaps, access constraints, and ethical visualization choices reflect the analyst’s methodical judgment and understanding of compliance to standard practices in conflict-zone and humanitarian geographical analysis. As these considerations are procedural and ethical in nature, no direct external citations were presented.
