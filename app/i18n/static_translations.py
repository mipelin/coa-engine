from __future__ import annotations

SUPPORTED_STATIC_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "nl", "pl", "tr", "cs", "ro", "hu", "bg", "hr", "sk", "sl", "et", "lv", "lt", "da", "no", "is", "fi", "sv", "sq", "mk", "me", "el"]

STATIC_UI_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {},
    "es": {
        "header.badge.disconnected": "Desconectado",
        "header.threat": "Amenaza",
        "scenario.baltic": "Mar Báltico",
        "scenario.arctic": "Ártico",
        "scenario.mediterranean": "Mediterráneo",
        "btn.start": "Iniciar",
        "btn.stop": "Detener",
        "subheader.what": "Qué es esto:",
        "subheader.what.text": "un entorno de apoyo a la decisión en vivo que ingiere contactos sintéticos, actualiza el estado de amenaza, genera COAs consultivas, simula resultados y recomienda un paquete.",
        "guide.step1": "1. Seleccionar escenario",
        "guide.step2": "2. Pulsar Iniciar",
        "guide.step3": "3. Observar cómo cambian contactos y amenaza",
        "guide.step4": "4. Revisar COAs / paquete",
        "guide.step5": "5. Usar el Simulador para inyectar o editar unidades",
        "guide.step6": "6. Generar briefing",
        "why.changed": "Qué cambió",
        "map.style": "Estilo de mapa",
        "map.style.osm_standard": "OpenStreetMap estándar",
        "map.style.osm_humanitarian": "OSM humanitario",
        "map.style.carto_light": "Carto claro",
        "map.style.carto_dark": "Carto oscuro",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrar unidades",
        "map.filter.friendly": "Aliadas",
        "map.filter.hostile": "Hostiles",
        "map.filter.neutral": "Neutrales",
        "map.filter.air": "Aéreas",
        "map.filter.naval": "Navales",
        "map.filter.land": "Terrestres",
        "map.filter.infra": "Infraestructura",
        "map.filter.cable_routes": "Mostrar rutas de cable",
        "map.filter.noaa_traffic": "Mostrar tráfico NOAA replay",
        "tab.guide": "Guía",
        "tab.contacts": "Contactos",
        "tab.coas": "COAs",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulador",
        "tab.log": "Registro",
        "guide.how_title": "Cómo funciona el sistema",
        "guide.how.1": "El motor emite o recibe contactos como buques, UAV, reportes de interferencia y eventos de cable.",
        "guide.how.2": "Cada nuevo contacto actualiza el estado en vivo y el historial de contactos.",
        "guide.how.3": "El bucle de análisis recalcula indicadores de anomalía y probabilidades de amenaza por entidad.",
        "guide.how.4": "El motor de COA genera opciones basadas en reglas. No permite que el LLM invente acciones.",
        "guide.how.5": "Cada COA se simula y puntúa. Después el asignador comprueba si un paquete coordinado de varias COAs es realmente viable con los medios actuales.",
        "guide.how.6": "El sistema destaca la mejor recomendación y puede generar un briefing estilo comandante bajo demanda.",
        "guide.control_title": "Qué controlas",
        "guide.control.1": "<b>Escenario:</b> elige el área operativa sintética y la evolución guionizada de la amenaza.",
        "guide.control.2": "<b>Iniciar / Detener:</b> inicia o detiene el bucle de ticks en vivo.",
        "guide.control.3": "<b>Mapa:</b> el lado izquierdo muestra siempre la imagen actual de contactos.",
        "guide.control.4": "<b>Tráfico NOAA Replay:</b> capa opcional de trazas AIS históricas de NOAA reubicadas en el escenario para comportamiento de demo.",
        "guide.control.5": "<b>Simulador:</b> inyecta, edita, elimina o guioniza el comportamiento de unidades.",
        "guide.control.6": "<b>Briefing:</b> genera una explicación legible de la recomendación actual.",
        "guide.steps_title": "Paso a paso",
        "guide.steps.1": "Abre este dashboard y elige un escenario en la barra superior.",
        "guide.steps.2": "Pulsa <b>Iniciar</b>. El motor comienza a avanzar y la situación evoluciona.",
        "guide.steps.3": "Observa el mapa a la izquierda y el indicador de <b>Amenaza</b> en la cabecera. Si salta a ALTA o CRÍTICA, el análisis detectó un cambio relevante.",
        "guide.steps.4": "Abre <b>Contactos</b> para ver unidades activas y banderas de alerta.",
        "guide.steps.5": "Abre <b>COAs</b> para revisar opciones clasificadas. Si existe un paquete coordinado, aparece encima de las COAs individuales.",
        "guide.steps.6": "Abre <b>Simulador</b> si quieres colocar una nueva unidad en el mapa o forzar una maniobra, interferencia o aproximación.",
        "guide.steps.7": "Pulsa <b>Generar briefing</b> cuando quieras un resumen operativo conciso.",
        "guide.callout.major_change": "¿Qué cuenta como un cambio importante?",
        "guide.callout.major_change.text": "Ejemplos: un buque gira hacia infraestructura, merodea cerca de un cable, aparece un UAV cerca del aeropuerto, se emite una interferencia o cambia la COA recomendada.",
        "guide.callout.bundle_q": "¿Qué es un paquete?",
        "guide.callout.bundle_a": "Un paquete es simplemente varias COAs consultivas que tienen sentido juntas, por ejemplo sombra + ISR + protección de cable. No es un modo separado ni misterioso.",
        "guide.callout.not_doing": "Lo que el sistema no hace:",
        "guide.callout.not_doing.text": "no ejecuta órdenes, no asigna armas y no autoriza enfrentamientos de forma autónoma.",
        "contacts.stat.contacts": "Contactos",
        "contacts.stat.tracks": "Trazas",
        "contacts.stat.coas": "COAs",
        "contacts.stat.processed": "Procesados",
        "briefing.generate": "Generar briefing",
        "briefing.download_pdf": "Descargar PDF",
        "briefing.download_pdf_en": "Descargar PDF (EN)",
        "sim.quick_scenarios": "Escenarios rápidos",
        "sim.quick_desc": "Usa estos presets si quieres que el motor reaccione de forma visible. Los contactos hostiles y desconocidos elevan la presión. La patrulla y el ISR aliados mejoran el apoyo disponible y pueden desbloquear paquetes coordinados más fuertes.",
        "sim.play.maritime_threat": "Amenaza marítima cerca del cable",
        "sim.play.maritime_threat.desc": "Inyecta un buque hostil cerca de infraestructura con AIS apagado y comportamiento sospechoso a baja velocidad",
        "sim.play.uav_airport": "UAV cerca del aeropuerto",
        "sim.play.uav_airport.desc": "Inyecta un UAV hostil con firma de riesgo de espacio aéreo",
        "sim.play.ew_escalation": "Escalada EW",
        "sim.play.ew_escalation.desc": "Inyecta una fuente de interferencia en el área operativa actual",
        "sim.play.allied_isr": "Añadir apoyo ISR aliado",
        "sim.play.allied_isr.desc": "Inyecta un UAV/activo de apoyo amigo para probar cambios de postura",
        "sim.play.allied_patrol": "Añadir patrulla aliada",
        "sim.play.allied_patrol.desc": "Inyecta un buque de patrulla aliado en la zona",
        "sim.play.cable_alert": "Incidente de infraestructura",
        "sim.play.cable_alert.desc": "Inyecta una alerta tipo evento de cable cerca del centro del mapa",
        "sim.undo_last": "Deshacer última inyección",
        "sim.reset_scenario": "Reiniciar escenario",
        "sim.preset.suspicious_vessel": "Buque sospechoso",
        "sim.preset.suspicious_vessel.desc": "Buque hostil cerca del centro actual del mapa",
        "sim.preset.hostile_uav": "UAV hostil",
        "sim.preset.hostile_uav.desc": "UAV con firma de amenaza elevada",
        "sim.preset.jamming_event": "Evento de interferencia",
        "sim.preset.jamming_event.desc": "Inyecta un contacto de interferencia que afecta a las anomalías",
        "sim.preset.cable_event": "Evento de cable",
        "sim.preset.cable_event.desc": "Inyecta un evento tipo rotura de cable",
        "sim.quick.add_suspicious": "Añadir buque sospechoso ahora",
        "sim.quick.add_suspicious.desc": "Contacto marítimo hostil inmediato en el centro del mapa",
        "sim.quick.add_uav": "Añadir UAV hostil ahora",
        "sim.quick.add_uav.desc": "Contacto aéreo inmediato cerca de la zona actual",
        "sim.quick.trigger_jamming": "Activar interferencia ahora",
        "sim.quick.trigger_jamming.desc": "Anomalía tipo EW inmediata en la zona actual",
        "sim.quick.trigger_cable": "Activar alerta de cable ahora",
        "sim.quick.trigger_cable.desc": "Incidente de infraestructura inmediato cerca del centro del mapa",
        "sim.show_advanced": "Mostrar colocación avanzada",
        "sim.form.name": "Nombre",
        "sim.form.type": "Tipo",
        "sim.form.allegiance": "Afiliación",
        "sim.form.speed": "Velocidad (kts)",
        "sim.form.heading": "Rumbo",
        "sim.form.latitude": "Latitud",
        "sim.form.longitude": "Longitud",
        "sim.form.jamming_radius": "Radio de interferencia (mn)",
        "sim.form.ais_off": "AIS apagado",
        "sim.form.position": "Posición",
        "sim.form.add_unit": "Añadir unidad",
        "sim.form.cancel": "Cancelar",
        "sim.option.vessel": "Buque",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarino",
        "sim.option.convoy": "Convoy",
        "sim.option.jamming": "Interferencia",
        "sim.option.cable_event": "Evento de cable",
        "sim.option.hostile": "Hostil",
        "sim.option.friendly": "Aliada",
        "sim.option.neutral": "Neutral",
        "tab.query": "Consultar",
        "query.disclaimer_title": "Solo informativo.",
        "query.disclaimer_body": "El LLM explica; los pronósticos se basan en simulación. Las respuestas no autorizan decisiones ni acciones.",
        "query.input_placeholder": "Pregunte sobre la situación actual, una COA o un escenario hipotético...",
        "query.ask_btn": "Consultar",
        "query.busy": "Pensando...",
        "query.error": "Error",
        "query.no_answer": "No se obtuvo respuesta.",
        "query.meta.llm": "Asistido por LLM",
        "query.meta.deterministic": "Determinista",
        "query.meta.forecast": "Pronóstico / Escenario hipotético",
        "query.sources": "Fuentes:",
        "query.forecast_results": "Resultados del pronóstico",
        "query.forecast.threat_trend": "Tendencia de amenaza",
        "query.forecast.confidence": "Confianza",
        "query.forecast.threat_level": "Nivel de amenaza",
        "query.forecast.contacts": "Contactos",
        "query.forecast.horizon": "Horizonte",
        "query.forecast.ticks": "ticks",
        "query.forecast.key_risks": "Riesgos clave:",
        "query.forecast.stimuli_fired": "Estímulos ejecutados:",
        "query.trend.increase": "aumento",
        "query.trend.decrease": "disminución",
        "query.trend.stable": "estable",
        "query.chip.threat_label": "Nivel de amenaza",
        "query.chip.threat_question": "¿Cuál es el nivel de amenaza actual?",
        "query.chip.coa_label": "¿Por qué esta COA?",
        "query.chip.coa_question": "¿Por qué se recomienda esta COA?",
        "query.chip.changed_label": "¿Qué cambió?",
        "query.chip.changed_question": "¿Qué cambió recientemente?",
        "query.chip.roe_label": "Estado ROE",
        "query.chip.roe_question": "¿Qué COAs requieren autorización?",
        "query.chip.cable_label": "Hipótesis: cable",
        "query.chip.cable_question": "¿Qué pasa si se corta el cable?",
        "query.chip.outcome_label": "Resultado COA",
        "query.chip.outcome_question": "¿Qué ocurre si elegimos la COA recomendada?",
    },
    "fr": {
        "header.badge.disconnected": "Déconnecté",
        "header.threat": "Menace",
        "scenario.baltic": "Mer Baltique",
        "scenario.arctic": "Arctique",
        "scenario.mediterranean": "Méditerranée",
        "btn.start": "Démarrer",
        "btn.stop": "Arrêter",
        "subheader.what": "Qu'est-ce que c'est :",
        "subheader.what.text": "un environnement de soutien à la décision en temps réel qui ingère des contacts synthétiques, met à jour l'état de la menace, génère des COA consultatifs, simule des résultats et recommande un paquet.",
        "guide.step1": "1. Sélectionner un scénario",
        "guide.step2": "2. Cliquer sur Démarrer",
        "guide.step3": "3. Observer l'évolution des contacts et de la menace",
        "guide.step4": "4. Examiner les COA / le paquet",
        "guide.step5": "5. Utiliser le Simulateur pour injecter ou modifier des unités",
        "guide.step6": "6. Générer un briefing",
        "why.changed": "Ce qui a changé",
        "map.style": "Style de carte",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM humanitaire",
        "map.style.carto_light": "Carto clair",
        "map.style.carto_dark": "Carto sombre",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrer les unités",
        "map.filter.friendly": "Amis",
        "map.filter.hostile": "Ennemis",
        "map.filter.neutral": "Neutres",
        "map.filter.air": "Aériens",
        "map.filter.naval": "Navals",
        "map.filter.land": "Terrestres",
        "map.filter.infra": "Infrastructure",
        "map.filter.cable_routes": "Afficher les routes de câble",
        "map.filter.noaa_traffic": "Afficher le replay du trafic NOAA",
        "tab.guide": "Guide",
        "tab.contacts": "Contacts",
        "tab.coas": "COA",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulateur",
        "tab.log": "Journal",
        "guide.how_title": "Comment fonctionne le système",
        "guide.how.1": "Le moteur émet ou reçoit des contacts tels que des navires, UAV, rapports d'interférence et événements de câble.",
        "guide.how.2": "Chaque nouveau contact met à jour l'état en direct et l'historique des contacts.",
        "guide.how.3": "La boucle d'analyse recalcule les indicateurs d'anomalie et les probabilités de menace par entité.",
        "guide.how.4": "Le moteur de COA génère des options basées sur des règles. Il n'autorise pas le LLM à inventer des actions.",
        "guide.how.5": "Chaque COA est simulée et notée. Ensuite, l'assignateur vérifie si un paquet coordonné de plusieurs COA est réellement viable avec les moyens actuels.",
        "guide.how.6": "Le système met en évidence la meilleure recommandation et peut générer un briefing de style commandant à la demande.",
        "guide.control_title": "Ce que vous contrôlez",
        "guide.control.1": "<b>Scénario :</b> choisissez la zone opérationnelle synthétique et l'évolution scénarisée de la menace.",
        "guide.control.2": "<b>Démarrer / Arrêter :</b> démarre ou arrête la boucle de ticks en direct.",
        "guide.control.3": "<b>Carte :</b> le côté gauche montre toujours l'image actuelle des contacts.",
        "guide.control.4": "<b>Replay Trafic NOAA :</b> couche optionnelle de traces AIS historiques de NOAA repositionnées dans le scénario pour un comportement de démo.",
        "guide.control.5": "<b>Simulateur :</b> injecte, modifie, supprime ou scénarise le comportement des unités.",
        "guide.control.6": "<b>Briefing :</b> génère une explication lisible de la recommandation actuelle.",
        "guide.steps_title": "Étape par étape",
        "guide.steps.1": "Ouvrez ce tableau de bord et choisissez un scénario dans la barre supérieure.",
        "guide.steps.2": "Cliquez sur <b>Démarrer</b>. Le moteur commence à avancer et la situation évolue.",
        "guide.steps.3": "Observez la carte à gauche et l'indicateur de <b>Menace</b> dans l'en-tête. Si elle passe à ÉLEVÉE ou CRITIQUE, l'analyse a détecté un changement pertinent.",
        "guide.steps.4": "Ouvrez <b>Contacts</b> pour voir les unités actives et les alertes.",
        "guide.steps.5": "Ouvrez <b>COA</b> pour examiner les options classifiées. Si un paquet coordonné existe, il apparaît au-dessus des COA individuelles.",
        "guide.steps.6": "Ouvrez <b>Simulateur</b> si vous souhaitez placer une nouvelle unité sur la carte ou forcer une manœuvre, une interférence ou une approche.",
        "guide.steps.7": "Cliquez sur <b>Générer briefing</b> lorsque vous souhaitez un résumé opérationnel concis.",
        "guide.callout.major_change": "Qu'est-ce qui compte comme un changement important ?",
        "guide.callout.major_change.text": "Exemples : un navire tourne vers une infrastructure, rôde près d'un câble, un UAV apparaît près de l'aéroport, une interférence est émise ou la COA recommandée change.",
        "guide.callout.bundle_q": "Qu'est-ce qu'un paquet ?",
        "guide.callout.bundle_a": "Un paquet est simplement plusieurs COA consultatives qui ont du sens ensemble, par exemple ombre + ISR + protection de câble. Ce n'est pas un mode séparé ou mystérieux.",
        "guide.callout.not_doing": "Ce que le système ne fait pas :",
        "guide.callout.not_doing.text": "il n'exécute pas d'ordres, n'attribue pas d'armes et n'autorise pas les engagements de manière autonome.",
        "contacts.stat.contacts": "Contacts",
        "contacts.stat.tracks": "Trajectoires",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Traités",
        "briefing.generate": "Générer briefing",
        "briefing.download_pdf": "Télécharger PDF",
        "briefing.download_pdf_en": "Télécharger PDF (EN)",
        "sim.quick_scenarios": "Scénarios rapides",
        "sim.quick_desc": "Utilisez ces préréglages si vous voulez que le moteur réagisse de manière visible. Les contacts hostiles et inconnus augmentent la pression. La patrouille et l'ISR amis améliorent le soutien disponible et peuvent débloquer des paquets coordonnés plus solides.",
        "sim.play.maritime_threat": "Menace maritime près du câble",
        "sim.play.maritime_threat.desc": "Injecte un navire hostile près d'une infrastructure avec AIS éteint et comportement suspect à basse vitesse",
        "sim.play.uav_airport": "UAV près de l'aéroport",
        "sim.play.uav_airport.desc": "Injecte un UAV hostile avec signature de risque d'espace aérien",
        "sim.play.ew_escalation": "Escalade EW",
        "sim.play.ew_escalation.desc": "Injecte une source d'interférence dans la zone opérationnelle actuelle",
        "sim.play.allied_isr": "Ajouter soutien ISR allié",
        "sim.play.allied_isr.desc": "Injecte un UAV/actif de soutien ami pour tester les changements de posture",
        "sim.play.allied_patrol": "Ajouter patrouille alliée",
        "sim.play.allied_patrol.desc": "Injecte un navire de patrouille allié dans la zone",
        "sim.play.cable_alert": "Incident d'infrastructure",
        "sim.play.cable_alert.desc": "Injecte une alerte de type événement de câble près du centre de la carte",
        "sim.undo_last": "Annuler dernière injection",
        "sim.reset_scenario": "Réinitialiser scénario",
        "sim.preset.suspicious_vessel": "Navire suspect",
        "sim.preset.suspicious_vessel.desc": "Navire hostile près du centre actuel de la carte",
        "sim.preset.hostile_uav": "UAV hostile",
        "sim.preset.hostile_uav.desc": "UAV avec signature de menace élevée",
        "sim.preset.jamming_event": "Événement d'interférence",
        "sim.preset.jamming_event.desc": "Injecte un contact d'interférence affectant les anomalies",
        "sim.preset.cable_event": "Événement de câble",
        "sim.preset.cable_event.desc": "Injecte un événement de type rupture de câble",
        "sim.quick.add_suspicious": "Ajouter navire suspect maintenant",
        "sim.quick.add_suspicious.desc": "Contact maritime hostile immédiat au centre de la carte",
        "sim.quick.add_uav": "Ajouter UAV hostile maintenant",
        "sim.quick.add_uav.desc": "Contact aérien immédiat près de la zone actuelle",
        "sim.quick.trigger_jamming": "Activer l'interférence maintenant",
        "sim.quick.trigger_jamming.desc": "Anomalie de type EW immédiate dans la zone actuelle",
        "sim.quick.trigger_cable": "Activer l'alerte de câble maintenant",
        "sim.quick.trigger_cable.desc": "Incident d'infrastructure immédiat près du centre de la carte",
        "sim.show_advanced": "Afficher la configuration avancée",
        "sim.form.name": "Nom",
        "sim.form.type": "Type",
        "sim.form.allegiance": "Affiliation",
        "sim.form.speed": "Vitesse (kts)",
        "sim.form.heading": "Cap",
        "sim.form.latitude": "Latitude",
        "sim.form.longitude": "Longitude",
        "sim.form.jamming_radius": "Rayon d'interférence (mn)",
        "sim.form.ais_off": "AIS désactivé",
        "sim.form.position": "Position",
        "sim.form.add_unit": "Ajouter unité",
        "sim.form.cancel": "Annuler",
        "sim.option.vessel": "Navire",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Sous-marin",
        "sim.option.convoy": "Convoi",
        "sim.option.jamming": "Interférence",
        "sim.option.cable_event": "Événement de câble",
        "sim.option.hostile": "Hostile",
        "sim.option.friendly": "Amis",
        "sim.option.neutral": "Neutre"
    },
    "de": {
        "header.badge.disconnected": "Getrennt",
        "header.threat": "Bedrohung",
        "scenario.baltic": "Ostsee",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Mittelmeer",
        "btn.start": "Starten",
        "btn.stop": "Stoppen",
        "subheader.what": "Was ist das:",
        "subheader.what.text": "eine Live-Entscheidungsunterstützungsumgebung, die synthetische Kontakte aufnimmt, den Bedrohungsstatus aktualisiert, beratende COAs generiert, Ergebnisse simuliert und ein Paket empfiehlt.",
        "guide.step1": "1. Szenario auswählen",
        "guide.step2": "2. Starten drücken",
        "guide.step3": "3. Beobachten, wie Kontakte und Bedrohung sich ändern",
        "guide.step4": "4. COAs / Paket überprüfen",
        "guide.step5": "5. Simulator verwenden, um Einheiten zu injizieren oder zu bearbeiten",
        "guide.step6": "6. Briefing generieren",
        "why.changed": "Was sich geändert hat",
        "map.style": "Kartenstil",
        "map.style.osm_standard": "OpenStreetMap Standard",
        "map.style.osm_humanitarian": "OSM Humanitär",
        "map.style.carto_light": "Carto Hell",
        "map.style.carto_dark": "Carto Dunkel",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Einheiten filtern",
        "map.filter.friendly": "Verbündete",
        "map.filter.hostile": "Feindlich",
        "map.filter.neutral": "Neutral",
        "map.filter.air": "Luft",
        "map.filter.naval": "Seefahrt",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastruktur",
        "map.filter.cable_routes": "Kabelrouten anzeigen",
        "map.filter.noaa_traffic": "NOAA-Verkehrs-Replay anzeigen",
        "tab.guide": "Anleitung",
        "tab.contacts": "Kontakte",
        "tab.coas": "COAs",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Protokoll",
        "guide.how_title": "Wie das System funktioniert",
        "guide.how.1": "Der Motor emittiert oder empfängt Kontakte wie Schiffe, UAVs, Interferenzberichte und Kabelereignisse.",
        "guide.how.2": "Jeder neue Kontakt aktualisiert den Live-Status und die Kontakthistorie.",
        "guide.how.3": "Die Analyse-Schleife berechnet neu Anomalieindikatoren und Bedrohungswahrscheinlichkeiten pro Entität.",
        "guide.how.4": "Der COA-Motor generiert Optionen basierend auf Regeln. Er erlaubt es dem LLM nicht, Aktionen zu erfinden.",
        "guide.how.5": "Jede COA wird simuliert und bewertet. Danach prüft der Zuweiser, ob ein koordiniertes Paket mehrerer COAs mit den aktuellen Mitteln tatsächlich durchführbar ist.",
        "guide.how.6": "Das System hebt die beste Empfehlung hervor und kann bei Bedarf ein Kommandobriefing generieren.",
        "guide.control_title": "Was Sie steuern",
        "guide.control.1": "<b>Szenario:</b> Wählen Sie das synthetische Einsatzgebiet und die geskriptete Bedrohungsevolutionslinie.",
        "guide.control.2": "<b>Starten / Stoppen:</b> Startet oder stoppt die Live-Tick-Schleife.",
        "guide.control.3": "<b>Karte:</b> Die linke Seite zeigt immer das aktuelle Kontaktbild.",
        "guide.control.4": "<b>NOAA-Verkehrs-Replay:</b> Optionale Schicht historischer AIS-Spuren von NOAA, die für Demo-Verhalten im Szenario neu positioniert sind.",
        "guide.control.5": "<b>Simulator:</b> Injiziert, bearbeitet, löscht oder skriptet das Verhalten von Einheiten.",
        "guide.control.6": "<b>Briefing:</b> Generiert eine lesbare Erklärung der aktuellen Empfehlung.",
        "guide.steps_title": "Schritt für Schritt",
        "guide.steps.1": "Öffnen Sie dieses Dashboard und wählen Sie oben ein Szenario aus.",
        "guide.steps.2": "Drücken Sie <b>Starten</b>. Der Motor beginnt voranzukommen und die Situation entwickelt sich.",
        "guide.steps.3": "Beobachten Sie die Karte links und den <b>Bedrohungs</b>-Indikator oben. Wenn er auf HOCH oder KRITISCH springt, hat die Analyse eine relevante Änderung erkannt.",
        "guide.steps.4": "Öffnen Sie <b>Kontakte</b>, um aktive Einheiten und Alarmflaggen anzuzeigen.",
        "guide.steps.5": "Öffnen Sie <b>COAs</b>, um klassifizierte Optionen zu überprüfen. Wenn ein koordiniertes Paket existiert, erscheint es über den einzelnen COAs.",
        "guide.steps.6": "Öffnen Sie <b>Simulator</b>, wenn Sie eine neue Einheit auf der Karte platzieren oder eine Manöver-, Interferenz- oder Annäherungsbewegung erzwingen möchten.",
        "guide.steps.7": "Drücken Sie <b>Briefing generieren</b>, wenn Sie eine prägnante operative Zusammenfassung wünschen.",
        "guide.callout.major_change": "Was zählt als wichtige Änderung?",
        "guide.callout.major_change.text": "Beispiele: Ein Schiff dreht sich zur Infrastruktur, kreist in der Nähe eines Kabels, ein UAV erscheint in der Nähe des Flughafens, es wird eine Interferenz gesendet oder die empfohlene COA ändert sich.",
        "guide.callout.bundle_q": "Was ist ein Paket?",
        "guide.callout.bundle_a": "Ein Paket ist einfach mehrere beratende COAs, die zusammen sinnvoll sind, z. B. Schatten + ISR + Kabelschutz. Es ist kein separater oder mysteriöser Modus.",
        "guide.callout.not_doing": "Was das System nicht tut:",
        "guide.callout.not_doing.text": "Es führt Befehle nicht aus, weist keine Waffen zu und autorisiert keine Gefechte autonom.",
        "contacts.stat.contacts": "Kontakte",
        "contacts.stat.tracks": "Spuren",
        "contacts.stat.coas": "COAs",
        "contacts.stat.processed": "Verarbeitet",
        "briefing.generate": "Briefing generieren",
        "briefing.download_pdf": "PDF herunterladen",
        "briefing.download_pdf_en": "PDF herunterladen (EN)",
        "sim.quick_scenarios": "Schnelle Szenarien",
        "sim.quick_desc": "Verwenden Sie diese Presets, wenn Sie möchten, dass der Motor sichtbar reagiert. Feindliche und unbekannte Kontakte erhöhen den Druck. Verbündete Patrouillen und ISR verbessern die verfügbare Unterstützung und können stärkere koordinierte Pakete freischalten.",
        "sim.play.maritime_threat": "Maritime Bedrohung nahe Kabel",
        "sim.play.maritime_threat.desc": "Injiziert ein feindliches Schiff nahe der Infrastruktur mit ausgeschaltetem AIS und verdächtigem Verhalten bei niedriger Geschwindigkeit",
        "sim.play.uav_airport": "UAV nahe Flughafen",
        "sim.play.uav_airport.desc": "Injiziert ein feindliches UAV mit Luftraum-Risikosignatur",
        "sim.play.ew_escalation": "EW-Eskalation",
        "sim.play.ew_escalation.desc": "Injiziert eine Interferenzquelle im aktuellen Einsatzgebiet",
        "sim.play.allied_isr": "Verbündete ISR-Unterstützung hinzufügen",
        "sim.play.allied_isr.desc": "Injiziert ein freundliches UAV/Unterstützungselement, um Posturwechsel zu testen",
        "sim.play.allied_patrol": "Verbündete Patrouille hinzufügen",
        "sim.play.allied_patrol.desc": "Injiziert ein verbündetes Patrouillenschiff in das Gebiet",
        "sim.play.cable_alert": "Infrastrukturvorfall",
        "sim.play.cable_alert.desc": "Injiziert einen Kabelereignis-Alarm nahe dem Kartenmittelpunkt",
        "sim.undo_last": "Letzte Injektion rückgängig machen",
        "sim.reset_scenario": "Szenario zurücksetzen",
        "sim.preset.suspicious_vessel": "Verdächtiges Schiff",
        "sim.preset.suspicious_vessel.desc": "Feindliches Schiff nahe dem aktuellen Kartenmittelpunkt",
        "sim.preset.hostile_uav": "Feindliches UAV",
        "sim.preset.hostile_uav.desc": "UAV mit erhöhter Bedrohungssignatur",
        "sim.preset.jamming_event": "Interferenzereignis",
        "sim.preset.jamming_event.desc": "Injiziert einen Interferenzkontakt, der Anomalien beeinflusst",
        "sim.preset.cable_event": "Kabelereignis",
        "sim.preset.cable_event.desc": "Injiziert ein Kabelbruch-Ereignis",
        "sim.quick.add_suspicious": "Jetzt verdächtiges Schiff hinzufügen",
        "sim.quick.add_suspicious.desc": "Sofortiger feindlicher maritimer Kontakt im Kartenmittelpunkt",
        "sim.quick.add_uav": "Jetzt feindliches UAV hinzufügen",
        "sim.quick.add_uav.desc": "Sofortiger Luftkontakt in der aktuellen Zone",
        "sim.quick.trigger_jamming": "Jetzt Interferenz auslösen",
        "sim.quick.trigger_jamming.desc": "Sofortige EW-Anomalie in der aktuellen Zone",
        "sim.quick.trigger_cable": "Jetzt Kabelalarm auslösen",
        "sim.quick.trigger_cable.desc": "Sofortiger Infrastrukturvorfall nahe dem Kartenmittelpunkt",
        "sim.show_advanced": "Erweiterte Platzierung anzeigen",
        "sim.form.name": "Name",
        "sim.form.type": "Typ",
        "sim.form.allegiance": "Zugehörigkeit",
        "sim.form.speed": "Geschw. (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Breitengrad",
        "sim.form.longitude": "Längengrad",
        "sim.form.jamming_radius": "Interferenzradius (nm)",
        "sim.form.ais_off": "AIS aus",
        "sim.form.position": "Position",
        "sim.form.add_unit": "Einheit hinzufügen",
        "sim.form.cancel": "Abbrechen",
        "sim.option.vessel": "Schiff",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "U-Boot",
        "sim.option.convoy": "Konvoi",
        "sim.option.jamming": "Interferenz",
        "sim.option.cable_event": "Kabelereignis",
        "sim.option.hostile": "Feindlich",
        "sim.option.friendly": "Verbündet",
        "sim.option.neutral": "Neutral"
    },
    "it": {
        "header.badge.disconnected": "Disconnesso",
        "header.threat": "Minaccia",
        "scenario.baltic": "Mar Baltico",
        "scenario.arctic": "Artico",
        "scenario.mediterranean": "Mediterraneo",
        "btn.start": "Avvia",
        "btn.stop": "Ferma",
        "subheader.what": "Cos'è questo:",
        "subheader.what.text": "un ambiente di supporto decisionale live che ingerisce contatti sintetici, aggiorna lo stato della minaccia, genera COA consultive, simula risultati e raccomanda un pacchetto.",
        "guide.step1": "1. Seleziona scenario",
        "guide.step2": "2. Premi Avvia",
        "guide.step3": "3. Osserva come cambiano contatti e minaccia",
        "guide.step4": "4. Rivedi COA / pacchetto",
        "guide.step5": "5. Usa il Simulatore per iniettare o modificare unità",
        "guide.step6": "6. Genera briefing",
        "why.changed": "Cosa è cambiato",
        "map.style": "Stile mappa",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM umanitario",
        "map.style.carto_light": "Carto chiaro",
        "map.style.carto_dark": "Carto scuro",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtra unità",
        "map.filter.friendly": "Alleati",
        "map.filter.hostile": "Nemici",
        "map.filter.neutral": "Neutri",
        "map.filter.air": "Aerei",
        "map.filter.naval": "Navali",
        "map.filter.land": "Terrestri",
        "map.filter.infra": "Infrastruttura",
        "map.filter.cable_routes": "Mostra rotte cavo",
        "map.filter.noaa_traffic": "Mostra replay traffico NOAA",
        "tab.guide": "Guida",
        "tab.contacts": "Contatti",
        "tab.coas": "COA",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulatore",
        "tab.log": "Registro",
        "guide.how_title": "Come funziona il sistema",
        "guide.how.1": "Il motore emette o riceve contatti come navi, UAV, rapporti di interferenza ed eventi di cavo.",
        "guide.how.2": "Ogni nuovo contatto aggiorna lo stato live e la cronologia dei contatti.",
        "guide.how.3": "Il ciclo di analisi ricalcola gli indicatori di anomalia e le probabilità di minaccia per entità.",
        "guide.how.4": "Il motore COA genera opzioni basate su regole. Non permette al LLM di inventare azioni.",
        "guide.how.5": "Ogni COA viene simulata e valutata. Successivamente, l'assegnatore verifica se un pacchetto coordinato di diverse COA è realmente fattibile con i mezzi attuali.",
        "guide.how.6": "Il sistema evidenzia la migliore raccomandazione e può generare un briefing stile comandante su richiesta.",
        "guide.control_title": "Cosa controlli",
        "guide.control.1": "<b>Scenario:</b> scegli l'area operativa sintetica e l'evoluzione guionizzata della minaccia.",
        "guide.control.2": "<b>Avvia / Ferma:</b> avvia o ferma il ciclo di tick live.",
        "guide.control.3": "<b>Mappa:</b> il lato sinistro mostra sempre l'immagine attuale dei contatti.",
        "guide.control.4": "<b>Replay Traffico NOAA:</b> strato opzionale di tracce AIS storiche di NOAA riposizionate nello scenario per comportamento demo.",
        "guide.control.5": "<b>Simulatore:</b> inietta, modifica, elimina o guionizza il comportamento delle unità.",
        "guide.control.6": "<b>Briefing:</b> genera una spiegazione leggibile della raccomandazione attuale.",
        "guide.steps_title": "Passo dopo passo",
        "guide.steps.1": "Apri questa dashboard e scegli uno scenario nella barra superiore.",
        "guide.steps.2": "Premi <b>Avvia</b>. Il motore inizia ad avanzare e la situazione evolve.",
        "guide.steps.3": "Osserva la mappa a sinistra e l'indicatore <b>Minaccia</b> nell'intestazione. Se salta a ALTA o CRITICA, l'analisi ha rilevato un cambiamento rilevante.",
        "guide.steps.4": "Apri <b>Contatti</b> per vedere unità attive e bandiere di allerta.",
        "guide.steps.5": "Apri <b>COA</b> per rivedere le opzioni classificate. Se esiste un pacchetto coordinato, appare sopra le COA individuali.",
        "guide.steps.6": "Apri <b>Simulatore</b> se vuoi posizionare una nuova unità sulla mappa o forzare una manovra, interferenza o avvicinamento.",
        "guide.steps.7": "Premi <b>Genera briefing</b> quando desideri un riepilogo operativo conciso.",
        "guide.callout.major_change": "Cosa conta come cambiamento importante?",
        "guide.callout.major_change.text": "Esempi: una nave gira verso un'infrastruttura, vaga vicino a un cavo, appare un UAV vicino all'aeroporto, viene emessa un'interferenza o cambia la COA raccomandata.",
        "guide.callout.bundle_q": "Cos'è un pacchetto?",
        "guide.callout.bundle_a": "Un pacchetto è semplicemente diverse COA consultive che hanno senso insieme, ad esempio ombreggiamento + ISR + protezione cavo. Non è una modalità separata o misteriosa.",
        "guide.callout.not_doing": "Cosa non fa il sistema:",
        "guide.callout.not_doing.text": "non esegue ordini, non assegna armi e non autorizza combattimenti in modo autonomo.",
        "contacts.stat.contacts": "Contatti",
        "contacts.stat.tracks": "Tracce",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Elaborati",
        "briefing.generate": "Genera briefing",
        "briefing.download_pdf": "Scarica PDF",
        "briefing.download_pdf_en": "Scarica PDF (EN)",
        "sim.quick_scenarios": "Scenari rapidi",
        "sim.quick_desc": "Usa questi preset se vuoi che il motore reagisca in modo visibile. I contatti nemici e sconosciuti aumentano la pressione. La pattuglia e l'ISR alleati migliorano il supporto disponibile e possono sbloccare pacchetti coordinati più forti.",
        "sim.play.maritime_threat": "Minaccia marittima vicino al cavo",
        "sim.play.maritime_threat.desc": "Inietta una nave nemica vicino a un'infrastruttura con AIS spento e comportamento sospetto a bassa velocità",
        "sim.play.uav_airport": "UAV vicino all'aeroporto",
        "sim.play.uav_airport.desc": "Inietta un UAV nemico con firma di rischio aereo",
        "sim.play.ew_escalation": "Escalation EW",
        "sim.play.ew_escalation.desc": "Inietta una fonte di interferenza nell'area operativa attuale",
        "sim.play.allied_isr": "Aggiungi supporto ISR alleato",
        "sim.play.allied_isr.desc": "Inietta un UAV/attivo di supporto amico per testare cambiamenti di postura",
        "sim.play.allied_patrol": "Aggiungi pattuglia alleata",
        "sim.play.allied_patrol.desc": "Inietta una nave di pattuglia alleata nella zona",
        "sim.play.cable_alert": "Incidente infrastruttura",
        "sim.play.cable_alert.desc": "Inietta un avviso tipo evento cavo vicino al centro della mappa",
        "sim.undo_last": "Annulla ultima iniezione",
        "sim.reset_scenario": "Resetta scenario",
        "sim.preset.suspicious_vessel": "Nave sospetta",
        "sim.preset.suspicious_vessel.desc": "Nave nemica vicino al centro attuale della mappa",
        "sim.preset.hostile_uav": "UAV nemico",
        "sim.preset.hostile_uav.desc": "UAV con firma di minaccia elevata",
        "sim.preset.jamming_event": "Evento di interferenza",
        "sim.preset.jamming_event.desc": "Inietta un contatto di interferenza che influenza le anomalie",
        "sim.preset.cable_event": "Evento cavo",
        "sim.preset.cable_event.desc": "Inietta un evento tipo rottura di cavo",
        "sim.quick.add_suspicious": "Aggiungi nave sospetta ora",
        "sim.quick.add_suspicious.desc": "Contatto marittimo nemico immediato al centro della mappa",
        "sim.quick.add_uav": "Aggiungi UAV nemico ora",
        "sim.quick.add_uav.desc": "Contatto aereo immediato vicino alla zona attuale",
        "sim.quick.trigger_jamming": "Attiva interferenza ora",
        "sim.quick.trigger_jamming.desc": "Anomalia tipo EW immediata nella zona attuale",
        "sim.quick.trigger_cable": "Attiva allerta cavo ora",
        "sim.quick.trigger_cable.desc": "Incidente infrastruttura immediato vicino al centro della mappa",
        "sim.show_advanced": "Mostra posizionamento avanzato",
        "sim.form.name": "Nome",
        "sim.form.type": "Tipo",
        "sim.form.allegiance": "Affiliazione",
        "sim.form.speed": "Velocità (kts)",
        "sim.form.heading": "Rumbo",
        "sim.form.latitude": "Latitudine",
        "sim.form.longitude": "Longitudine",
        "sim.form.jamming_radius": "Raggio interferenza (mn)",
        "sim.form.ais_off": "AIS spento",
        "sim.form.position": "Posizione",
        "sim.form.add_unit": "Aggiungi unità",
        "sim.form.cancel": "Annulla",
        "sim.option.vessel": "Nave",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Sottomarino",
        "sim.option.convoy": "Convoglio",
        "sim.option.jamming": "Interferenza",
        "sim.option.cable_event": "Evento cavo",
        "sim.option.hostile": "Nemico",
        "sim.option.friendly": "Alleato",
        "sim.option.neutral": "Neutro"
    },
    "pt": {
        "header.badge.disconnected": "Desconectado",
        "header.threat": "Ameaça",
        "scenario.baltic": "Mar Báltico",
        "scenario.arctic": "Ártico",
        "scenario.mediterranean": "Mediterrâneo",
        "btn.start": "Iniciar",
        "btn.stop": "Parar",
        "subheader.what": "O que é isto:",
        "subheader.what.text": "um ambiente de apoio à decisão em tempo real que ingere contatos sintéticos, atualiza o estado de ameaça, gera COAs consultivas, simula resultados e recomenda um pacote.",
        "guide.step1": "1. Selecionar cenário",
        "guide.step2": "2. Clicar em Iniciar",
        "guide.step3": "3. Observar a mudança de contatos e ameaça",
        "guide.step4": "4. Revisar COAs / pacote",
        "guide.step5": "5. Usar o Simulador para injetar ou editar unidades",
        "guide.step6": "6. Gerar briefing",
        "why.changed": "O que mudou",
        "map.style": "Estilo do mapa",
        "map.style.osm_standard": "OpenStreetMap padrão",
        "map.style.osm_humanitarian": "OSM humanitário",
        "map.style.carto_light": "Carto claro",
        "map.style.carto_dark": "Carto escuro",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrar unidades",
        "map.filter.friendly": "Aliados",
        "map.filter.hostile": "Hostis",
        "map.filter.neutral": "Neutros",
        "map.filter.air": "Aéreos",
        "map.filter.naval": "Navais",
        "map.filter.land": "Terrestres",
        "map.filter.infra": "Infraestrutura",
        "map.filter.cable_routes": "Mostrar rotas de cabo",
        "map.filter.noaa_traffic": "Mostrar replay de tráfego NOAA",
        "tab.guide": "Guia",
        "tab.contacts": "Contatos",
        "tab.coas": "COAs",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulador",
        "tab.log": "Registro",
        "guide.how_title": "Como o sistema funciona",
        "guide.how.1": "O motor emite ou recebe contatos como navios, UAV, relatórios de interferência e eventos de cabo.",
        "guide.how.2": "Cada novo contato atualiza o estado em tempo real e o histórico de contatos.",
        "guide.how.3": "O ciclo de análise recalcula indicadores de anomalia e probabilidades de ameaça por entidade.",
        "guide.how.4": "O motor de COA gera opções baseadas em regras. Não permite que o LLM invente ações.",
        "guide.how.5": "Cada COA é simulada e pontuada. Depois, o alocador verifica se um pacote coordenado de várias COAs é realmente viável com os meios atuais.",
        "guide.how.6": "O sistema destaca a melhor recomendação e pode gerar um briefing estilo comandante sob demanda.",
        "guide.control_title": "O que você controla",
        "guide.control.1": "<b>Cenário:</b> escolha a área operacional sintética e a evolução guionizada da ameaça.",
        "guide.control.2": "<b>Iniciar / Parar:</b> inicia ou para o ciclo de ticks em tempo real.",
        "guide.control.3": "<b>Mapa:</b> o lado esquerdo sempre mostra a imagem atual de contatos.",
        "guide.control.4": "<b>Replay de Tráfego NOAA:</b> camada opcional de rastros AIS históricos da NOAA realocados no cenário para comportamento de demonstração.",
        "guide.control.5": "<b>Simulador:</b> injeta, edita, elimina ou guioniza o comportamento de unidades.",
        "guide.control.6": "<b>Briefing:</b> gera uma explicação legível da recomendação atual.",
        "guide.steps_title": "Passo a passo",
        "guide.steps.1": "Abra este dashboard e escolha um cenário na barra superior.",
        "guide.steps.2": "Clique em <b>Iniciar</b>. O motor começa a avançar e a situação evolui.",
        "guide.steps.3": "Observe o mapa à esquerda e o indicador de <b>Ameaça</b> no cabeçalho. Se saltar para ALTA ou CRÍTICA, a análise detectou uma mudança relevante.",
        "guide.steps.4": "Abra <b>Contatos</b> para ver unidades ativas e bandeiras de alerta.",
        "guide.steps.5": "Abra <b>COAs</b> para revisar opções classificadas. Se existir um pacote coordenado, ele aparece acima das COAs individuais.",
        "guide.steps.6": "Abra <b>Simulador</b> se quiser colocar uma nova unidade no mapa ou forçar uma manobra, interferência ou aproximação.",
        "guide.steps.7": "Clique em <b>Gerar briefing</b> quando quiser um resumo operacional conciso.",
        "guide.callout.major_change": "O que conta como uma mudança importante?",
        "guide.callout.major_change.text": "Exemplos: um navio vira em direção à infraestrutura, vagueia perto de um cabo, aparece um UAV perto do aeroporto, é emitida uma interferência ou a COA recomendada muda.",
        "guide.callout.bundle_q": "O que é um pacote?",
        "guide.callout.bundle_a": "Um pacote é simplesmente várias COAs consultivas que fazem sentido juntas, por exemplo sombra + ISR + proteção de cabo. Não é um modo separado nem misterioso.",
        "guide.callout.not_doing": "O que o sistema não faz:",
        "guide.callout.not_doing.text": "não executa ordens, não aloca armas e não autoriza confrontos de forma autônoma.",
        "contacts.stat.contacts": "Contatos",
        "contacts.stat.tracks": "Rastros",
        "contacts.stat.coas": "COAs",
        "contacts.stat.processed": "Processados",
        "briefing.generate": "Gerar briefing",
        "briefing.download_pdf": "Baixar PDF",
        "briefing.download_pdf_en": "Baixar PDF (EN)",
        "sim.quick_scenarios": "Cenários rápidos",
        "sim.quick_desc": "Use estes presets se quiser que o motor reaja de forma visível. Contatos hostis e desconhecidos aumentam a pressão. Patrulha e ISR aliados melhoram o apoio disponível e podem desbloquear pacotes coordenados mais fortes.",
        "sim.play.maritime_threat": "Ameaça marítima perto do cabo",
        "sim.play.maritime_threat.desc": "Injeta um navio hostil perto da infraestrutura com AIS desligado e comportamento suspeito em baixa velocidade",
        "sim.play.uav_airport": "UAV perto do aeroporto",
        "sim.play.uav_airport.desc": "Injeta um UAV hostil com assinatura de risco de espaço aéreo",
        "sim.play.ew_escalation": "Escalada EW",
        "sim.play.ew_escalation.desc": "Injeta uma fonte de interferência na área operacional atual",
        "sim.play.allied_isr": "Adicionar apoio ISR aliado",
        "sim.play.allied_isr.desc": "Injeta um UAV/ativo de apoio amigo para testar mudanças de postura",
        "sim.play.allied_patrol": "Adicionar patrulha aliada",
        "sim.play.allied_patrol.desc": "Injeta um navio de patrulha aliado na zona",
        "sim.play.cable_alert": "Incidente de infraestrutura",
        "sim.play.cable_alert.desc": "Injeta um alerta tipo evento de cabo perto do centro do mapa",
        "sim.undo_last": "Desfazer última injeção",
        "sim.reset_scenario": "Reiniciar cenário",
        "sim.preset.suspicious_vessel": "Navio suspeito",
        "sim.preset.suspicious_vessel.desc": "Navio hostil perto do centro atual do mapa",
        "sim.preset.hostile_uav": "UAV hostil",
        "sim.preset.hostile_uav.desc": "UAV com assinatura de ameaça elevada",
        "sim.preset.jamming_event": "Evento de interferência",
        "sim.preset.jamming_event.desc": "Injeta um contato de interferência que afeta as anomalias",
        "sim.preset.cable_event": "Evento de cabo",
        "sim.preset.cable_event.desc": "Injeta um evento tipo ruptura de cabo",
        "sim.quick.add_suspicious": "Adicionar navio suspeito agora",
        "sim.quick.add_suspicious.desc": "Contato marítimo hostil imediato no centro do mapa",
        "sim.quick.add_uav": "Adicionar UAV hostil agora",
        "sim.quick.add_uav.desc": "Contato aéreo imediato perto da zona atual",
        "sim.quick.trigger_jamming": "Ativar interferência agora",
        "sim.quick.trigger_jamming.desc": "Anomalia tipo EW imediata na zona atual",
        "sim.quick.trigger_cable": "Ativar alerta de cabo agora",
        "sim.quick.trigger_cable.desc": "Incidente de infraestrutura imediato perto do centro do mapa",
        "sim.show_advanced": "Mostrar colocação avançada",
        "sim.form.name": "Nome",
        "sim.form.type": "Tipo",
        "sim.form.allegiance": "Afiliação",
        "sim.form.speed": "Velocidade (kts)",
        "sim.form.heading": "Rumo",
        "sim.form.latitude": "Latitude",
        "sim.form.longitude": "Longitude",
        "sim.form.jamming_radius": "Raio de interferência (mn)",
        "sim.form.ais_off": "AIS desligado",
        "sim.form.position": "Posição",
        "sim.form.add_unit": "Adicionar unidade",
        "sim.form.cancel": "Cancelar",
        "sim.option.vessel": "Navio",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarino",
        "sim.option.convoy": "Convoio",
        "sim.option.jamming": "Interferência",
        "sim.option.cable_event": "Evento de cabo",
        "sim.option.hostile": "Hostil",
        "sim.option.friendly": "Aliado",
        "sim.option.neutral": "Neutro"
    },
    "nl": {
        "header.badge.disconnected": "Ontkoppeld",
        "header.threat": "Dreiging",
        "scenario.baltic": "Baltische Zee",
        "scenario.arctic": "Arctisch",
        "scenario.mediterranean": "Middellandse Zee",
        "btn.start": "Starten",
        "btn.stop": "Stoppen",
        "subheader.what": "Wat is dit:",
        "subheader.what.text": "een live beslissingsondersteuningsomgeving die synthetische contacten ingevoert, de dreigingsstatus bijwerkt, adviserende COA's genereert, resultaten simuleert en een pakket aanbeveelt.",
        "guide.step1": "1. Scenario selecteren",
        "guide.step2": "2. Op Start klikken",
        "guide.step3": "3. Observeren hoe contacten en dreiging veranderen",
        "guide.step4": "4. COA's / pakket bekijken",
        "guide.step5": "5. De Simulator gebruiken om eenheden in te voeren of te bewerken",
        "guide.step6": "6. Briefing genereren",
        "why.changed": "Wat is veranderd",
        "map.style": "Kaartstijl",
        "map.style.osm_standard": "OpenStreetMap standaard",
        "map.style.osm_humanitarian": "OSM humanitair",
        "map.style.carto_light": "Carto licht",
        "map.style.carto_dark": "Carto donker",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Eenheden filteren",
        "map.filter.friendly": "Bondgenoten",
        "map.filter.hostile": "Vijanden",
        "map.filter.neutral": "Neutraal",
        "map.filter.air": "Lucht",
        "map.filter.naval": "Maritiem",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastructuur",
        "map.filter.cable_routes": "Kabelroutes weergeven",
        "map.filter.noaa_traffic": "NOAA verkeer replay weergeven",
        "tab.guide": "Gids",
        "tab.contacts": "Contacten",
        "tab.coas": "COA's",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Log",
        "guide.how_title": "Hoe het systeem werkt",
        "guide.how.1": "De motor zendt of ontvangt contacten zoals schepen, UAV's, interferentie-rapporten en kabelgebeurtenissen.",
        "guide.how.2": "Elk nieuw contact werkt de live status en het contactgeschiedenis bij.",
        "guide.how.3": "De analysecyclus berekent anomalie-indicatoren en dreigingskansen per entiteit opnieuw.",
        "guide.how.4": "De COA-motor genereert opties op basis van regels. Het staat de LLM niet toe acties uit te vinden.",
        "guide.how.5": "Elke COA wordt gesimuleerd en beoordeeld. Daarna controleert de toewijzer of een gecoördineerd pakket van verschillende COA's daadwerkelijk uitvoerbaar is met de huidige middelen.",
        "guide.how.6": "Het systeem benadrukt de beste aanbeveling en kan op aanvraag een commandant-stijl briefing genereren.",
        "guide.control_title": "Wat u controleert",
        "guide.control.1": "<b>Scenario:</b> kiest het synthetische operationele gebied en de gescripte evolutie van de dreiging.",
        "guide.control.2": "<b>Starten / Stoppen:</b> startt of stopt de live tick-lus.",
        "guide.control.3": "<b>Kaart:</b> de linkerkant toont altijd de huidige contactafbeelding.",
        "guide.control.4": "<b>NOAA Verkeer Replay:</b> optionele laag van historische AIS-sporen van NOAA opnieuw geplaatst in het scenario voor demo-gedrag.",
        "guide.control.5": "<b>Simulator:</b> injecteert, bewerkt, verwijdert of scriptt het gedrag van eenheden.",
        "guide.control.6": "<b>Briefing:</b> genereert een leesbare uitleg van de huidige aanbeveling.",
        "guide.steps_title": "Stap voor stap",
        "guide.steps.1": "Open dit dashboard en selecteer een scenario in de bovenste balk.",
        "guide.steps.2": "Klik op <b>Starten</b>. De motor begint te vorderen en de situatie evolueert.",
        "guide.steps.3": "Observeer de kaart links en de <b>Dreiging</b> indicator in de header. Als deze naar HOOG of KRITIEK springt, heeft de analyse een relevante verandering gedetecteerd.",
        "guide.steps.4": "Open <b>Contacten</b> om actieve eenheden en waarschuwingsvlaggen te zien.",
        "guide.steps.5": "Open <b>COA's</b> om geclassificeerde opties te bekijken. Als er een gecoördineerd pakket is, verschijnt dit boven de individuele COA's.",
        "guide.steps.6": "Open <b>Simulator</b> als u een nieuwe eenheid op de kaart wilt plaatsen of een manoeuvre, interferentie of nadering wilt forceren.",
        "guide.steps.7": "Klik op <b>Briefing genereren</b> wanneer u een beknopte operationele samenvatting wilt.",
        "guide.callout.major_change": "Wat telt als een belangrijke verandering?",
        "guide.callout.major_change.text": "Voorbeelden: een schip draait naar infrastructuur, cirkelt nabij een kabel, een UAV verschijnt nabij de luchthaven, er wordt interferentie uitgezonden of de aanbevolen COA verandert.",
        "guide.callout.bundle_q": "Wat is een pakket?",
        "guide.callout.bundle_a": "Een pakket is simpelweg verschillende adviserende COA's die samen zinvol zijn, bijvoorbeeld schaduw + ISR + kabelbescherming. Het is geen aparte of mysterieuze modus.",
        "guide.callout.not_doing": "Wat het systeem niet doet:",
        "guide.callout.not_doing.text": "het voert bevelen niet uit, wijst wapens niet toe en autoriseert gevechten niet autonoom.",
        "contacts.stat.contacts": "Contacten",
        "contacts.stat.tracks": "Sporen",
        "contacts.stat.coas": "COA's",
        "contacts.stat.processed": "Verwerkt",
        "briefing.generate": "Briefing genereren",
        "briefing.download_pdf": "PDF downloaden",
        "briefing.download_pdf_en": "PDF downloaden (EN)",
        "sim.quick_scenarios": "Snelle scenario's",
        "sim.quick_desc": "Gebruik deze presets als u wilt dat de motor zichtbaar reageert. Vijandige en onbekende contacten verhogen de druk. Bondgenoot patrouille en ISR verbeteren de beschikbare ondersteuning en kunnen sterkere gecoördineerde pakketten ontgrendelen.",
        "sim.play.maritime_threat": "Maritieme dreiging nabij kabel",
        "sim.play.maritime_threat.desc": "Injecteert een vijandig schip nabij infrastructuur met uitgeschakelde AIS en verdacht laag tempo gedrag",
        "sim.play.uav_airport": "UAV nabij luchthaven",
        "sim.play.uav_airport.desc": "Injecteert een vijandige UAV met luchtruimte risicoprofiel",
        "sim.play.ew_escalation": "EW-escalatie",
        "sim.play.ew_escalation.desc": "Injecteert een interferentiebron in het huidige operationele gebied",
        "sim.play.allied_isr": "Voeg bondgenoot ISR toe",
        "sim.play.allied_isr.desc": "Injecteert een UAV/vriendelijke ondersteuningsactief om postuurveranderingen te testen",
        "sim.play.allied_patrol": "Voeg bondgenoot patrouille toe",
        "sim.play.allied_patrol.desc": "Injecteert een bondgenoot patrouilleschip in het gebied",
        "sim.play.cable_alert": "Infrastructuurincident",
        "sim.play.cable_alert.desc": "Injecteert een kabelgebeurtenis-type waarschuwing nabij het midden van de kaart",
        "sim.undo_last": "Laatste injectie ongedaan maken",
        "sim.reset_scenario": "Scenario resetten",
        "sim.preset.suspicious_vessel": "Verdacht schip",
        "sim.preset.suspicious_vessel.desc": "Vijandig schip nabij het huidige midden van de kaart",
        "sim.preset.hostile_uav": "Vijandige UAV",
        "sim.preset.hostile_uav.desc": "UAV met verhoogd dreigingsprofiel",
        "sim.preset.jamming_event": "Interferentiegebeurtenis",
        "sim.preset.jamming_event.desc": "Injecteert een interferentiecontact dat anomalieën beïnvloedt",
        "sim.preset.cable_event": "Kabelgebeurtenis",
        "sim.preset.cable_event.desc": "Injecteert een kabelbreuk-type gebeurtenis",
        "sim.quick.add_suspicious": "Nu verdacht schip toevoegen",
        "sim.quick.add_suspicious.desc": "Onmiddellijk vijandig maritiem contact in het midden van de kaart",
        "sim.quick.add_uav": "Nu UAV toevoegen",
        "sim.quick.add_uav.desc": "Onmiddellijk luchtcontact nabij het huidige gebied",
        "sim.quick.trigger_jamming": "Nu interferentie activeren",
        "sim.quick.trigger_jamming.desc": "Onmiddellijke EW-anomalie in het huidige gebied",
        "sim.quick.trigger_cable": "Nu kabelwaarschuwing activeren",
        "sim.quick.trigger_cable.desc": "Onmiddellijk infrastructuurincident nabij het midden van de kaart",
        "sim.show_advanced": "Geavanceerde plaatsing tonen",
        "sim.form.name": "Naam",
        "sim.form.type": "Type",
        "sim.form.allegiance": "Affiliatie",
        "sim.form.speed": "Snelheid (kts)",
        "sim.form.heading": "Koers",
        "sim.form.latitude": "Breedtegraad",
        "sim.form.longitude": "Lengtegraad",
        "sim.form.jamming_radius": "Interferentieradius (mn)",
        "sim.form.ais_off": "AIS uit",
        "sim.form.position": "Positie",
        "sim.form.add_unit": "Eenheid toevoegen",
        "sim.form.cancel": "Annuleren",
        "sim.option.vessel": "Schip",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Onderzeeër",
        "sim.option.convoy": "Konvooi",
        "sim.option.jamming": "Interferentie",
        "sim.option.cable_event": "Kabelgebeurtenis",
        "sim.option.hostile": "Vijandig",
        "sim.option.friendly": "Bondgenoot",
        "sim.option.neutral": "Neutraal"
    },
    "pl": {
        "header.badge.disconnected": "Odłączony",
        "header.threat": "Zagrożenie",
        "scenario.baltic": "Bałtyk",
        "scenario.arctic": "Arktyka",
        "scenario.mediterranean": "Morze Śródziemne",
        "btn.start": "Rozpocznij",
        "btn.stop": "Zatrzymaj",
        "subheader.what": "Czym to jest:",
        "subheader.what.text": "żywe środowisko wsparcia decyzyjnego, które pobiera syntetyczne kontakty, aktualizuje stan zagrożenia, generuje doradcze COA, symuluje wyniki i rekomenduje pakiet.",
        "guide.step1": "1. Wybierz scenariusz",
        "guide.step2": "2. Kliknij Rozpocznij",
        "guide.step3": "3. Obserwuj zmianę kontaktów i zagrożenia",
        "guide.step4": "4. Przejrzyj COA / pakiet",
        "guide.step5": "5. Użyj Symulatora do wstrzykiwania lub edytowania jednostek",
        "guide.step6": "6. Wygeneruj briefing",
        "why.changed": "Co się zmieniło",
        "map.style": "Styl mapy",
        "map.style.osm_standard": "Standardowy OSM",
        "map.style.osm_humanitarian": "Humanitarny OSM",
        "map.style.carto_light": "Jasny Carto",
        "map.style.carto_dark": "Ciemny Carto",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtruj jednostki",
        "map.filter.friendly": "Sprzymierzeńcy",
        "map.filter.hostile": "Wrogowie",
        "map.filter.neutral": "Neutralni",
        "map.filter.air": "Lotnicze",
        "map.filter.naval": "Marynarki",
        "map.filter.land": "Lądowe",
        "map.filter.infra": "Infrastruktura",
        "map.filter.cable_routes": "Pokaż trasy kabli",
        "map.filter.noaa_traffic": "Pokaż odtwarzanie ruchu NOAA",
        "tab.guide": "Przewodnik",
        "tab.contacts": "Kontakty",
        "tab.coas": "COA",
        "tab.briefing": "Briefing",
        "tab.simulator": "Symulator",
        "tab.log": "Log",
        "guide.how_title": "Jak działa system",
        "guide.how.1": "Silnik emituje lub odbiera kontakty jako statki, UAV, raporty zakłóceń i zdarzenia kablowe.",
        "guide.how.2": "Każdy nowy kontakt aktualizuje stan na żywo i historię kontaktów.",
        "guide.how.3": "Pętla analityczna przelicza wskaźniki anomalii i prawdopodobieństwa zagrożenia dla każdej jednostki.",
        "guide.how.4": "Silnik COA generuje opcje na podstawie reguł. Nie pozwala LLM na wymyślanie działań.",
        "guide.how.5": "Każdy COA jest symulowany i oceniany. Następnie przypisujący sprawdza, czy skoordynowany pakiet wielu COA jest faktycznie wykonalny przy obecnych zasobach.",
        "guide.how.6": "System wyróżnia najlepszą rekomendację i może wygenerować briefing w stylu dowódcy na żądanie.",
        "guide.control_title": "Co kontrolujesz",
        "guide.control.1": "<b>Scenariusz:</b> wybierz syntetyczną strefę operacyjną i scenariuszowaną ewolucję zagrożenia.",
        "guide.control.2": "<b>Rozpocznij / Zatrzymaj:</b> rozpoczyna lub zatrzymuje pętlę ticków na żywo.",
        "guide.control.3": "<b>Mapa:</b> lewa strona zawsze pokazuje aktualny obraz kontaktów.",
        "guide.control.4": "<b>Odtwarzanie ruchu NOAA:</b> opcjonalna warstwa historycznych śladów AIS NOAA przeniesionych na scenariusz dla celów demonstracyjnych.",
        "guide.control.5": "<b>Symulator:</b> wstrzykuje, edytuje, usuwa lub scenariuszuje zachowanie jednostek.",
        "guide.control.6": "<b>Briefing:</b> generuje czytelną wyjaśnienie aktualnej rekomendacji.",
        "guide.steps_title": "Krok po kroku",
        "guide.steps.1": "Otwórz ten pulpit i wybierz scenariusz w górnym pasku.",
        "guide.steps.2": "Kliknij <b>Rozpocznij</b>. Silnik zaczyna postępować, a sytuacja ewoluuje.",
        "guide.steps.3": "Obserwuj mapę po lewej i wskaźnik <b>Zagrożenia</b> w nagłówku. Jeśli wzrośnie do WYSOKIEGO lub KRYTYCZNEGO, analiza wykryła istotną zmianę.",
        "guide.steps.4": "Otwórz <b>Kontakty</b>, aby zobaczyć aktywne jednostki i flagi ostrzegawcze.",
        "guide.steps.5": "Otwórz <b>COA</b>, aby przejrzeć sklasyfikowane opcje. Jeśli istnieje pakiet skoordynowany, pojawi się nad indywidualnymi COA.",
        "guide.steps.6": "Otwórz <b>Symulator</b>, jeśli chcesz umieścić nową jednostkę na mapie lub wymusić manewr, zakłócenie lub podejście.",
        "guide.steps.7": "Kliknij <b>Wygeneruj briefing</b>, gdy chcesz zwięzłe podsumowanie operacyjne.",
        "guide.callout.major_change": "Co jest uważane za znaczącą zmianę?",
        "guide.callout.major_change.text": "Przykłady: statek skręca w kierunku infrastruktury, krąży w pobliżu kabla, pojawia się UAV w pobliżu lotniska, emitowane jest zakłócenie lub zmienia się rekomendowane COA.",
        "guide.callout.bundle_q": "Czym jest pakiet?",
        "guide.callout.bundle_a": "Pakiet to po prostu kilka doradczych COA, które mają sens razem, np. cień + ISR + ochrona kabla. To nie jest osobny ani tajemniczy tryb.",
        "guide.callout.not_doing": "Czego system nie robi:",
        "guide.callout.not_doing.text": "nie wykonuje rozkazów, nie przydziela broni i nie autoryzuje konfrontacji autonomicznie.",
        "contacts.stat.contacts": "Kontakty",
        "contacts.stat.tracks": "Ślady",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Przetworzone",
        "briefing.generate": "Wygeneruj briefing",
        "briefing.download_pdf": "Pobierz PDF",
        "briefing.download_pdf_en": "Pobierz PDF (EN)",
        "sim.quick_scenarios": "Szybkie scenariusze",
        "sim.quick_desc": "Użyj tych presetów, jeśli chcesz, aby silnik reagował widocznie. Wrogie i nieznane kontakty zwiększają presję. Patrolowanie i wsparcie ISR sprzymierzeńców poprawiają dostępną pomoc i mogą odblokować silniejsze, skoordynowane pakiety.",
        "sim.play.maritime_threat": "Zagrożenie morskie w pobliżu kabla",
        "sim.play.maritime_threat.desc": "Wstrzyknij wrogiego statku w pobliżu infrastruktury z wyłączonym AIS i podejrzanym zachowaniem przy niskiej prędkości",
        "sim.play.uav_airport": "UAV w pobliżu lotniska",
        "sim.play.uav_airport.desc": "Wstrzyknij wrogiego UAV z sygnaturą ryzyka dla przestrzeni powietrznej",
        "sim.play.ew_escalation": "Eskalacja EW",
        "sim.play.ew_escalation.desc": "Wstrzyknij źródło zakłóceń w aktualnym obszarze operacyjnym",
        "sim.play.allied_isr": "Dodaj wsparcie ISR sprzymierzeńców",
        "sim.play.allied_isr.desc": "Wstrzyknij przyjacielskie UAV/aktywny element wsparcia, aby przetestować zmiany postawy",
        "sim.play.allied_patrol": "Dodaj patrol sprzymierzeńców",
        "sim.play.allied_patrol.desc": "Wstrzyknij sprzymierzeńca patrolowego w strefę",
        "sim.play.cable_alert": "Incydent infrastrukturalny",
        "sim.play.cable_alert.desc": "Wstrzyknij alert typu zdarzenie kablowe w pobliżu centrum mapy",
        "sim.undo_last": "Odwinięcie ostatniego wstrzyknięcia",
        "sim.reset_scenario": "Reset scenariusza",
        "sim.preset.suspicious_vessel": "Podejrzany statek",
        "sim.preset.suspicious_vessel.desc": "Wrogi statek w pobliżu aktualnego centrum mapy",
        "sim.preset.hostile_uav": "Wrogi UAV",
        "sim.preset.hostile_uav.desc": "UAV z podwyższoną sygnaturą zagrożenia",
        "sim.preset.jamming_event": "Zdarzenie zakłóceń",
        "sim.preset.jamming_event.desc": "Wstrzyknij kontakt zakłóceń wpływający na anomalie",
        "sim.preset.cable_event": "Zdarzenie kablowe",
        "sim.preset.cable_event.desc": "Wstrzyknij zdarzenie typu zerwanie kabla",
        "sim.quick.add_suspicious": "Dodaj podejrzany statek teraz",
        "sim.quick.add_suspicious.desc": "Natychmiastowy wrogi kontakt morski w centrum mapy",
        "sim.quick.add_uav": "Dodaj wrogi UAV teraz",
        "sim.quick.add_uav.desc": "Natychmiastowy kontakt powietrzny w pobliżu aktualnej strefy",
        "sim.quick.trigger_jamming": "Aktywuj zakłócenia teraz",
        "sim.quick.trigger_jamming.desc": "Natychmiastowa anomalia typu EW w aktualnej strefie",
        "sim.quick.trigger_cable": "Aktywuj alert kablowy teraz",
        "sim.quick.trigger_cable.desc": "Natychmiastowy incydent infrastrukturalny w pobliżu centrum mapy",
        "sim.show_advanced": "Pokaż zaawansowane umieszczenie",
        "sim.form.name": "Nazwa",
        "sim.form.type": "Typ",
        "sim.form.allegiance": "Afiliacja",
        "sim.form.speed": "Prędkość (kts)",
        "sim.form.heading": "Kierunek",
        "sim.form.latitude": "Szerokość",
        "sim.form.longitude": "Długość",
        "sim.form.jamming_radius": "Promień zakłóceń (mn)",
        "sim.form.ais_off": "AIS wyłączone",
        "sim.form.position": "Pozycja",
        "sim.form.add_unit": "Dodaj jednostkę",
        "sim.form.cancel": "Anuluj",
        "sim.option.vessel": "Statek",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Nokowce",
        "sim.option.convoy": "Konwój",
        "sim.option.jamming": "Zakłócenia",
        "sim.option.cable_event": "Zdarzenie kablowe",
        "sim.option.hostile": "Wrogi",
        "sim.option.friendly": "Sprzymierzeniec",
        "sim.option.neutral": "Neutralny"
    },
    "tr": {
        "header.badge.disconnected": "Bağlantı Kesik",
        "header.threat": "Tehdit",
        "scenario.baltic": "Baltık Denizi",
        "scenario.arctic": "Arktik",
        "scenario.mediterranean": "Akdeniz",
        "btn.start": "Başlat",
        "btn.stop": "Durdur",
        "subheader.what": "Bu nedir:",
        "subheader.what.text": "Senteetik temasları alan, tehdit durumunu güncelleyen, danışmanlık COA'ları oluşturan, sonuçları simüle eden ve bir paket öneren canlı bir karar destek ortamıdır.",
        "guide.step1": "1. Senaryo seçin",
        "guide.step2": "2. Başlat'a basın",
        "guide.step3": "3. Temasların ve tehdidin nasıl değiştiğini gözlemleyin",
        "guide.step4": "4. COA'ları / paketi inceleyin",
        "guide.step5": "5. Birimleri enjekte etmek veya düzenlemek için Simülatörü kullanın",
        "guide.step6": "6. Brifing oluşturun",
        "why.changed": "Ne değişti",
        "map.style": "Harita stili",
        "map.style.osm_standard": "Standart OSM",
        "map.style.osm_humanitarian": "İnsani OSM",
        "map.style.carto_light": "Açık Carto",
        "map.style.carto_dark": "Koyu Carto",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Birimleri filtrele",
        "map.filter.friendly": "Müttefik",
        "map.filter.hostile": "Düşman",
        "map.filter.neutral": "Nötr",
        "map.filter.air": "Hava",
        "map.filter.naval": "Deniz",
        "map.filter.land": "Kara",
        "map.filter.infra": "Altyapı",
        "map.filter.cable_routes": "Kablo rotalarını göster",
        "map.filter.noaa_traffic": "NOAA trafiği tekrarını göster",
        "tab.guide": "Kılavuz",
        "tab.contacts": "Temaslar",
        "tab.coas": "COA'lar",
        "tab.briefing": "Brifing",
        "tab.simulator": "Simülatör",
        "tab.log": "Kayıt",
        "guide.how_title": "Sistem nasıl çalışır",
        "guide.how.1": "Motor, gemiler, UAV, parazit raporları ve kablo olayları gibi temasları yayınlar veya alır.",
        "guide.how.2": "Her yeni temas, canlı durumu ve temas geçmişini günceller.",
        "guide.how.3": "Analiz döngüsü, varlık başına anomali göstergelerini ve tehdit olasılıklarını yeniden hesaplar.",
        "guide.how.4": "COA motoru, kurallara dayalı seçenekler üretir. LLM'nin eylemler icat etmesine izin vermez.",
        "guide.how.5": "Her COA simüle edilir ve puanlanır. Ardından atama, mevcut araçlarla koordineli bir COA paketinin gerçekten uygulanabilir olup olmadığını kontrol eder.",
        "guide.how.6": "Sistem en iyi öneriyi vurgular ve isteğe bağlı olarak komutan tarzı bir brifing oluşturabilir.",
        "guide.control_title": "Neleri kontrol ediyorsunuz",
        "guide.control.1": "<b>Senaryo:</b> sentetik operasyonel alanı ve tehdidin senaryo bazlı evrimini seçin.",
        "guide.control.2": "<b>Başlat / Durdur:</b> canlı tik döngüsünü başlatır veya durdurur.",
        "guide.control.3": "<b>Harita:</b> sol taraf her zaman temasların mevcut görüntüsünü gösterir.",
        "guide.control.4": "<b>NOAA Trafiği Tekrarı:</b> demo davranışı için senaryoya yeniden konumlandırılmış tarihsel NOAA AIS izlerinin isteğe bağlı katmanı.",
        "guide.control.5": "<b>Simülatör:</b> birimleri enjekte eder, düzenler, siler veya davranışlarını senaryolaştırır.",
        "guide.control.6": "<b>Brifing:</b> mevcut önerinin okunabilir bir açıklamasını oluşturur.",
        "guide.steps_title": "Adım adım",
        "guide.steps.1": "Bu kontrol panelini açın ve üst çubuktan bir senaryo seçin.",
        "guide.steps.2": "<b>Başlat</b>'a basın. Motor ilerlemeye başlar ve durum evrilir.",
        "guide.steps.3": "Soldaki haritayı ve başlık çubuğundaki <b>Tehdit</b> göstergesini izleyin. YÜKSEK veya KRİTİK'e sıçrarsa, analiz önemli bir değişiklik tespit etmiştir.",
        "guide.steps.4": "Aktif birimleri ve uyarı bayraklarını görmek için <b>Temaslar</b>'ı açın.",
        "guide.steps.5": "Sınıflandırılmış seçenekleri incelemek için <b>COA'lar</b>'ı açın. Koordineli bir paket varsa, bireysel COA'ların üzerinde görünür.",
        "guide.steps.6": "Yeni bir birim yerleştirmek veya bir manevra, parazit veya yaklaşmayı zorlamak isterseniz <b>Simülatör</b>'ı açın.",
        "guide.steps.7": "Kısa bir operasyonel özet istediğinizde <b>Brifing oluştur</b>'a basın.",
        "guide.callout.major_change": "Ne önemli bir değişiklik sayılır?",
        "guide.callout.major_change.text": "Örnekler: bir gemi altyapıya doğru döner, bir kablo yakınında devriye gezer, havaalanı yakınında bir UAV belirir, bir parazit yayınlanır veya önerilen COA değişir.",
        "guide.callout.bundle_q": "Paket nedir?",
        "guide.callout.bundle_a": "Bir paket, birlikte anlamlı olan birkaç danışmanlık COA'sıdır; örneğin gölge + ISR + kablo koruması. Ayrı veya gizemli bir mod değildir.",
        "guide.callout.not_doing": "Sistemin yapmadığı şeyler:",
        "guide.callout.not_doing.text": "emirleri yürütmez, silah atamaz ve çatışmaları otonom olarak onaylamaz.",
        "contacts.stat.contacts": "Temaslar",
        "contacts.stat.tracks": "İzler",
        "contacts.stat.coas": "COA'lar",
        "contacts.stat.processed": "İşlenmiş",
        "briefing.generate": "Brifing oluştur",
        "briefing.download_pdf": "PDF İndir",
        "briefing.download_pdf_en": "PDF İndir (EN)",
        "sim.quick_scenarios": "Hızlı senaryolar",
        "sim.quick_desc": "Motorun görünür şekilde tepki vermesini istiyorsanız bu ön ayarları kullanın. Düşman ve bilinmeyen temaslar baskıyı artırır. Müttefik devriye ve ISR, mevcut desteği iyileştirir ve daha güçlü koordineli paketleri kilitleyebilir.",
        "sim.play.maritime_threat": "Kablo yakınında deniz tehdidi",
        "sim.play.maritime_threat.desc": "AIS kapalı ve düşük hızda şüpheli davranış gösteren altyapı yakınında düşman bir gemi enjekte et",
        "sim.play.uav_airport": "Havaalanı yakınında UAV",
        "sim.play.uav_airport.desc": "Hava sahası riskli imzaya sahip düşman bir UAV enjekte et",
        "sim.play.ew_escalation": "EW tırmanışı",
        "sim.play.ew_escalation.desc": "Mevcut operasyonel alana bir parazit kaynağı enjekte et",
        "sim.play.allied_isr": "Müttefik ISR desteği ekle",
        "sim.play.allied_isr.desc": "Duruş değişikliklerini test etmek için bir UAV/müttefik destek varlığı enjekte et",
        "sim.play.allied_patrol": "Müttefik devriye ekle",
        "sim.play.allied_patrol.desc": "Bölgeye müttefik bir devriye gemisi enjekte et",
        "sim.play.cable_alert": "Altyapı olayı",
        "sim.play.cable_alert.desc": "Harita merkezine yakın bir yerde kablo olayına benzer bir uyarı enjekte et",
        "sim.undo_last": "Son enjeksiyonu geri al",
        "sim.reset_scenario": "Senaryoyu sıfırla",
        "sim.preset.suspicious_vessel": "Şüpheli gemi",
        "sim.preset.suspicious_vessel.desc": "Haritanın mevcut merkezine yakın düşman gemi",
        "sim.preset.hostile_uav": "Düşman UAV",
        "sim.preset.hostile_uav.desc": "Yüksek tehdit imzasına sahip UAV",
        "sim.preset.jamming_event": "Parazit olayı",
        "sim.preset.jamming_event.desc": "Anomalileri etkileyen bir parazit teması enjekte et",
        "sim.preset.cable_event": "Kablo olayı",
        "sim.preset.cable_event.desc": "Kablo kopması benzeri bir olay enjekte et",
        "sim.quick.add_suspicious": "Şüpheli gemi ekle",
        "sim.quick.add_suspicious.desc": "Harita merkezinde anında düşman deniz teması",
        "sim.quick.add_uav": "Düşman UAV ekle",
        "sim.quick.add_uav.desc": "Mevcut bölgeye yakın anında hava teması",
        "sim.quick.trigger_jamming": "Şimdi parazit tetikle",
        "sim.quick.trigger_jamming.desc": "Mevcut bölgede anında EW benzeri anomali",
        "sim.quick.trigger_cable": "Şimdi kablo uyarısı tetikle",
        "sim.quick.trigger_cable.desc": "Harita merkezine yakın anında altyapı olayı",
        "sim.show_advanced": "Gelişmiş yerleşimi göster",
        "sim.form.name": "Adı",
        "sim.form.type": "Tip",
        "sim.form.allegiance": "Bağlılık",
        "sim.form.speed": "Hız (kts)",
        "sim.form.heading": "Yön",
        "sim.form.latitude": "Enlem",
        "sim.form.longitude": "Boylam",
        "sim.form.jamming_radius": "Parazit yarıçapı (mn)",
        "sim.form.ais_off": "AIS kapalı",
        "sim.form.position": "Konum",
        "sim.form.add_unit": "Birim ekle",
        "sim.form.cancel": "İptal",
        "sim.option.vessel": "Gemi",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Denizaltı",
        "sim.option.convoy": "Filo",
        "sim.option.jamming": "Parazit",
        "sim.option.cable_event": "Kablo olayı",
        "sim.option.hostile": "Düşman",
        "sim.option.friendly": "Müttefik",
        "sim.option.neutral": "Nötr"
    },
    "cs": {
        "header.badge.disconnected": "Odpojené",
        "header.threat": "Hrozba",
        "scenario.baltic": "Baltický moře",
        "scenario.arctic": "Arktický",
        "scenario.mediterranean": "Středozemní",
        "btn.start": "Startovat",
        "btn.stop": "Zastavit",
        "subheader.what": "Co je to:",
        "subheader.what.text": "živé prostředí pro podpoře rozhodování, které přijímá syntetické kontakty, aktualizuje stav hrozby, generuje konzultativní COA, simuluje výsledky a doporučuje balíček.",
        "guide.step1": "1. Vyberte scénář",
        "guide.step2": "2. Klikněte na Startovat",
        "guide.step3": "3. Sledujte změny kontaktů a hrozby",
        "guide.step4": "4. Prohlédněte COA / balíček",
        "guide.step5": "5. Použijte Simulátor k injekci nebo úpravě jednotek",
        "guide.step6": "6. Vygenerujte zpravu (briefing)",
        "why.changed": "Co se změnilo",
        "map.style": "Styl mapy",
        "map.style.osm_standard": "Standardní OSM",
        "map.style.osm_humanitarian": "Humanitární OSM",
        "map.style.carto_light": "Carto lehké",
        "map.style.carto_dark": "Carto tmavé",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrovat jednotky",
        "map.filter.friendly": "Spojatelé",
        "map.filter.hostile": "Hostilní",
        "map.filter.neutral": "Neutrální",
        "map.filter.air": "Vzdušné",
        "map.filter.naval": "Námořní",
        "map.filter.land": "Pozemní",
        "map.filter.infra": "Infrastruktura",
        "map.filter.cable_routes": "Zobrazit kabelové trasy",
        "map.filter.noaa_traffic": "Zobrazit NOAA replay provozu",
        "tab.guide": "Průvodce",
        "tab.contacts": "Kontakty",
        "tab.coas": "COA",
        "tab.briefing": "Zpráva",
        "tab.simulator": "Simulátor",
        "tab.log": "Log",
        "guide.how_title": "Jak funguje systém",
        "guide.how.1": "Motor vysílá nebo přijímá kontakty jako lodě, UAV, hlášení interference a kabelové události.",
        "guide.how.2": "Každý nový kontakt aktualizuje živý stav a historii kontaktů.",
        "guide.how.3": "Analytický cyklus přepočítá ukazatele anomálií a pravděpodobnosti hrozby pro entitu.",
        "guide.how.4": "Motor COA generuje možnosti na základě pravidel. Neumožňuje LLM vymýšlet akce.",
        "guide.how.5": "Každé COA je simulováno a hodnoceno. Poté ověřuje přiřadicí, zda je koordinovaný balíček více COA skutečně proveditelný s aktuálními prostředky.",
        "guide.how.6": "Systém zdůrazňuje nejlepší doporučení a může na vyžádání vygenerovat zprávu ve stylu velitele.",
        "guide.control_title": "Co ovládáte",
        "guide.control.1": "<b>Scénář:</b> vyberte syntetickou operační oblast a scénářovou evoluci hrozby.",
        "guide.control.2": "<b>Startovat / Zastavit:</b> spouští nebo zastavuje cyklus živých ticků.",
        "guide.control.3": "<b>Mapa:</b> levá strana vždy zobrazuje aktuální stav kontaktů.",
        "guide.control.4": "<b>NOAA Replay provoz:</b> volitelná vrstva historických AIS stop je přesunutá do scénáře pro demonstrační chování.",
        "guide.control.5": "<b>Simulátor:</b> injektuje, upravuje, odstraňuje nebo scénářizuje chování jednotek.",
        "guide.control.6": "<b>Zpráva:</b> generuje čitelný popis aktuálního doporučení.",
        "guide.steps_title": "Krok za krokem",
        "guide.steps.1": "Otevřete tento dashboard a vyberte scénář v horním panelu.",
        "guide.steps.2": "Klikněte na <b>Startovat</b>. Motor začne postupovat a situace se vyvíjí.",
        "guide.steps.3": "Sledujte mapu vlevo a indikátor <b>Hrozba</b> v hlavičce. Pokud se zvýší na VYSOKÁ nebo KRITICKÁ, analýza detekovala relevantní změnu.",
        "guide.steps.4": "Otevřete <b>Kontakty</b> k zobrazení aktivních jednotek a varovných signálů.",
        "guide.steps.5": "Otevřete <b>COA</b> k zhlédnutí klasifikovaných možností. Pokud existuje koordinovaný balíček, zobrazí se nad jednotlivými COA.",
        "guide.steps.6": "Otevřete <b>Simulátor</b>, pokud chcete přidat novou jednotku na mapu nebo vynutit manévr, interferenci nebo přiblížení.",
        "guide.steps.7": "Klikněte na <b>Vygenerovat zprávu</b>, když chcete stručné operační shrnutí.",
        "guide.callout.major_change": "Co se počítá jako významná změna?",
        "guide.callout.major_change.text": "Příklady: loď se otočí k infrastruktuře, králí se poblíž kabelu, objeví se UAV poblíž letiště, vysílá se interference nebo se změní doporučené COA.",
        "guide.callout.bundle_q": "Co je balíček?",
        "guide.callout.bundle_a": "Balíček je jednoduše několik konzultativních COA, které mají smysl společně, např. stín + ISR + ochrana kabelu. Není to samostatný nebo tajemný režim.",
        "guide.callout.not_doing": "Co systém nedělá:",
        "guide.callout.not_doing.text": "nevykonává rozkazy, nepřiřazuje zbraně a autonomně neautorizuje střety.",
        "contacts.stat.contacts": "Kontakty",
        "contacts.stat.tracks": "Stopky",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Zpracované",
        "briefing.generate": "Vygenerovat zprávu",
        "briefing.download_pdf": "Stáhnout PDF",
        "briefing.download_pdf_en": "Stáhnout PDF (EN)",
        "sim.quick_scenarios": "Rychlé scénáře",
        "sim.quick_desc": "Použijte tyto přednastavení, pokud chcete, aby motor reagoval viditelně. Hostilní a neznámé kontakty zvyšují tlak. Spojatelská patroula a ISR zlepšují dostupnou podporu a mohou odemknout silnější koordinované balíčky.",
        "sim.play.maritime_threat": "Mořská hrozba poblíž kabelu",
        "sim.play.maritime_threat.desc": "Injektuje hostilou loď poblíž infrastruktury s vypnutým AIS a podezřelým chováním při nízké rychlosti",
        "sim.play.uav_airport": "UAV poblíž letiště",
        "sim.play.uav_airport.desc": "Injektuje hostilou UAV s signálem rizika pro vzdušnou obranu",
        "sim.play.ew_escalation": "ES eskalace",
        "sim.play.ew_escalation.desc": "Injektuje zdroj interference v aktuální operační oblasti",
        "sim.play.allied_isr": "Přidat spojatelskou ISR podporu",
        "sim.play.allied_isr.desc": "Injektuje přátelské UAV/podporu pro testování změn postoje",
        "sim.play.allied_patrol": "Přidat spojatelskou patroulu",
        "sim.play.allied_patrol.desc": "Injektuje spojatelskou patrolovací loď do zóny",
        "sim.play.cable_alert": "Incident s infrastrukturou",
        "sim.play.cable_alert.desc": "Injektuje varování typu kabelová událost poblíž středu mapy",
        "sim.undo_last": "Zrušit poslední injekci",
        "sim.reset_scenario": "Resetovat scénář",
        "sim.preset.suspicious_vessel": "Podezřelá loď",
        "sim.preset.suspicious_vessel.desc": "Hostilá loď poblíž aktuálního středu mapy",
        "sim.preset.hostile_uav": "Hostilá UAV",
        "sim.preset.hostile_uav.desc": "UAV s zvýšeným signálem hrozby",
        "sim.preset.jamming_event": "Interferenční událost",
        "sim.preset.jamming_event.desc": "Injektuje kontakt interference ovlivňující anomálie",
        "sim.preset.cable_event": "Kabelová událost",
        "sim.preset.cable_event.desc": "Injektuje událost typu poruzení kabelu",
        "sim.quick.add_suspicious": "Přidat podezřelou loď nyní",
        "sim.quick.add_suspicious.desc": "Okamžitý hostilý mořský kontakt v centru mapy",
        "sim.quick.add_uav": "Přidat hostilou UAV nyní",
        "sim.quick.add_uav.desc": "Okamžitý vzdušný kontakt poblíž aktuální zóny",
        "sim.quick.trigger_jamming": "Aktivovat interferenci nyní",
        "sim.quick.trigger_jamming.desc": "Okamžitá EW anomálie v aktuální zóně",
        "sim.quick.trigger_cable": "Aktivovat kabelový varování nyní",
        "sim.quick.trigger_cable.desc": "Okamžitý incident s infrastrukturou poblíž středu mapy",
        "sim.show_advanced": "Zobrazit pokročilou konfiguraci",
        "sim.form.name": "Název",
        "sim.form.type": "Typ",
        "sim.form.allegiance": "Příslušnost",
        "sim.form.speed": "Rychlost (kts)",
        "sim.form.heading": "Směr",
        "sim.form.latitude": "Latituda",
        "sim.form.longitude": "Longituda",
        "sim.form.jamming_radius": "Poloměr interference (mn)",
        "sim.form.ais_off": "AIS vypnuté",
        "sim.form.position": "Pozice",
        "sim.form.add_unit": "Přidat jednotku",
        "sim.form.cancel": "Zrušit",
        "sim.option.vessel": "Loď",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Podkorvet",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interference",
        "sim.option.cable_event": "Kabelová událost",
        "sim.option.hostile": "Hostilní",
        "sim.option.friendly": "Spojatel",
        "sim.option.neutral": "Neutrální"
    },
    "ro": {
        "header.badge.disconnected": "Deconectat",
        "header.threat": "Amenințare",
        "scenario.baltic": "Marea Baltică",
        "scenario.arctic": "Arctic",
        "scenario.mediterranean": "Mediterana",
        "btn.start": "Începe",
        "btn.stop": "Opri",
        "subheader.what": "Ce este asta:",
        "subheader.what.text": "un mediu de sprijin decizional în timp real care ingerează contacte sintetice, actualizează starea amenințării, generează COA-uri consultative, simulează rezultate și recomandă un pachet.",
        "guide.step1": "1. Selectați scenariul",
        "guide.step2": "2. Apăsați Începe",
        "guide.step3": "3. Observați cum se schimbă contactele și amenințarea",
        "guide.step4": "4. Revizuiți COA-urile / pachetul",
        "guide.step5": "5. Folosiți Simulatorul pentru a injecta sau edita unități",
        "guide.step6": "6. Generați briefing",
        "why.changed": "Ce s-a schimbat",
        "map.style": "Stil hartă",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM umanitar",
        "map.style.carto_light": "Carto deschis",
        "map.style.carto_dark": "Carto închis",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrează unități",
        "map.filter.friendly": "Aliați",
        "map.filter.hostile": "Inamici",
        "map.filter.neutral": "Neutri",
        "map.filter.air": "Aeriene",
        "map.filter.naval": "Navale",
        "map.filter.land": "Terestre",
        "map.filter.infra": "Infrastructură",
        "map.filter.cable_routes": "Arată traseele de cablu",
        "map.filter.noaa_traffic": "Arată retransmisiunea NOAA",
        "tab.guide": "Ghid",
        "tab.contacts": "Contacte",
        "tab.coas": "COA-uri",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Jurnal",
        "guide.how_title": "Cum funcționează sistemul",
        "guide.how.1": "Motorul emite sau primește contacte ca nave, UAV, rapoarte de interferență și evenimente de cablu.",
        "guide.how.2": "Fiecare contact nou actualizează starea în timp real și istoricul de contacte.",
        "guide.how.3": "Buclele de analiză recalculează indicatorii de anomalie și probabilitățile de amenințare pe entitate.",
        "guide.how.4": "Motorul de COA generează opțiuni bazate pe reguli. Nu permite LLM-ului să inventeze acțiuni.",
        "guide.how.5": "Fiecare COA este simulat și evaluat. Apoi, alocatorul verifică dacă un pachet coordonat de mai multe COA-uri este cu adevărat viabil cu mijloacele actuale.",
        "guide.how.6": "Sistemul evidențiază cea mai bună recomandare și poate genera un briefing de tip comandant la cerere.",
        "guide.control_title": "Ce controlezi",
        "guide.control.1": "<b>Scenariu:</b> alegi zona operațională sintetică și evoluția guionată a amenințării.",
        "guide.control.2": "<b>Începe / Opri:</b> pornește sau oprește bucla de tick-uri în timp real.",
        "guide.control.3": "<b>Hartă:</b> partea stângă arată întotdeauna imaginea curentă a contactelor.",
        "guide.control.4": "<b>Retransmisiune NOAA:</b> strat opțional de trasee AIS istorice NOAA repositionate în scenariu pentru comportament de demonstrație.",
        "guide.control.5": "<b>Simulator:</b> injectează, editează, elimină sau guionizează comportamentul unităților.",
        "guide.control.6": "<b>Briefing:</b> generează o explicație lizibilă a recomandării actuale.",
        "guide.steps_title": "Pas cu pas",
        "guide.steps.1": "Deschideți acest dashboard și alegeți un scenariu din bara superioară.",
        "guide.steps.2": "Apăsați <b>Începe</b>. Motorul începe să progreseze și situația evoluează.",
        "guide.steps.3": "Observați harta din stânga și indicatorul de <b>Amenințare</b> din antet. Dacă sare la ALTA sau CRITICĂ, analiza a detectat o schimbare relevantă.",
        "guide.steps.4": "Deschideți <b>Contacte</b> pentru a vedea unitățile active și semnalele de alarmă.",
        "guide.steps.5": "Deschideți <b>COA-uri</b> pentru a revizui opțiunile clasificate. Dacă există un pachet coordonat, acesta apare deasupra COA-urilor individuale.",
        "guide.steps.6": "Deschideți <b>Simulator</b> dacă doriți să plasați o nouă unitate pe hartă sau să forțați o manevră, interferență sau apropiere.",
        "guide.steps.7": "Apăsați <b>Generare briefing</b> atunci când doriți un rezumat operațional concis.",
        "guide.callout.major_change": "Ce contează ca schimbare majoră?",
        "guide.callout.major_change.text": "Exemple: o navă se rotește spre infrastructură, patrulează lângă un cablu, apare un UAV lângă aeroport, se emite o interferență sau se schimbă COA-ul recomandat.",
        "guide.callout.bundle_q": "Ce este un pachet?",
        "guide.callout.bundle_a": "Un pachet este pur și simplu mai multe COA-uri consultative care au sens împreună, de exemplu umbră + ISR + protecție cablu. Nu este un mod separat sau misterios.",
        "guide.callout.not_doing": "Ce nu face sistemul:",
        "guide.callout.not_doing.text": "nu execută ordine, nu alocă arme și nu autorizează confruntări autonom.",
        "contacts.stat.contacts": "Contacte",
        "contacts.stat.tracks": "Traiectorii",
        "contacts.stat.coas": "COA-uri",
        "contacts.stat.processed": "Procesate",
        "briefing.generate": "Generează briefing",
        "briefing.download_pdf": "Descarcă PDF",
        "briefing.download_pdf_en": "Descarcă PDF (EN)",
        "sim.quick_scenarios": "Scenarii rapide",
        "sim.quick_desc": "Folosiți aceste presetări dacă doriți ca motorul să reacționeze vizibil. Contactele inamice și necunoscute cresc presiunea. Patrularea și ISR-ul aliaților îmbunătățesc sprijinul disponibil și pot debloca pachete coordonate mai puternice.",
        "sim.play.maritime_threat": "Amenințare maritimă lângă cablu",
        "sim.play.maritime_threat.desc": "Injectează o navă inamică lângă infrastructură cu AIS oprit și comportament suspect la viteză mică",
        "sim.play.uav_airport": "UAV lângă aeroport",
        "sim.play.uav_airport.desc": "Injectează un UAV inamic cu semnătură de risc aerian",
        "sim.play.ew_escalation": "Escaladare EW",
        "sim.play.ew_escalation.desc": "Injectează o sursă de interferență în zona operațională curentă",
        "sim.play.allied_isr": "Adaugă sprijin ISR aliat",
        "sim.play.allied_isr.desc": "Injectează un UAV/activ de sprijin prieten pentru a testa schimbările de postură",
        "sim.play.allied_patrol": "Adaugă patrulă aliată",
        "sim.play.allied_patrol.desc": "Injectează o navă de patrulă aliată în zonă",
        "sim.play.cable_alert": "Incident de infrastructură",
        "sim.play.cable_alert.desc": "Injectează o alarmă de tip eveniment de cablu lângă centrul hărții",
        "sim.undo_last": "Anulează ultima injecție",
        "sim.reset_scenario": "Resetează scenariul",
        "sim.preset.suspicious_vessel": "Navă suspectă",
        "sim.preset.suspicious_vessel.desc": "Navă inamică lângă centrul curent al hărții",
        "sim.preset.hostile_uav": "UAV inamic",
        "sim.preset.hostile_uav.desc": "UAV cu semnătură de amenințare ridicată",
        "sim.preset.jamming_event": "Eveniment de interferență",
        "sim.preset.jamming_event.desc": "Injectează un contact de interferență care afectează anomaliile",
        "sim.preset.cable_event": "Eveniment de cablu",
        "sim.preset.cable_event.desc": "Injectează un eveniment de tip rupere de cablu",
        "sim.quick.add_suspicious": "Adaugă navă suspectă acum",
        "sim.quick.add_suspicious.desc": "Contact maritim inamic imediat în centrul hărții",
        "sim.quick.add_uav": "Adaugă UAV inamic acum",
        "sim.quick.add_uav.desc": "Contact aerian imediat lângă zona curentă",
        "sim.quick.trigger_jamming": "Activează interferența acum",
        "sim.quick.trigger_jamming.desc": "Anomalie de tip EW imediat în zona curentă",
        "sim.quick.trigger_cable": "Activează alerta de cablu acum",
        "sim.quick.trigger_cable.desc": "Incident de infrastructură imediat lângă centrul hărții",
        "sim.show_advanced": "Arată plasare avansată",
        "sim.form.name": "Nume",
        "sim.form.type": "Tip",
        "sim.form.allegiance": "Afiliere",
        "sim.form.speed": "Viteză (kts)",
        "sim.form.heading": "Rumb",
        "sim.form.latitude": "Latitudine",
        "sim.form.longitude": "Longitudine",
        "sim.form.jamming_radius": "Radiu de interferență (mn)",
        "sim.form.ais_off": "AIS oprit",
        "sim.form.position": "Poziție",
        "sim.form.add_unit": "Adaugă unitate",
        "sim.form.cancel": "Anulează",
        "sim.option.vessel": "Navă",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarin",
        "sim.option.convoy": "Convoy",
        "sim.option.jamming": "Interferență",
        "sim.option.cable_event": "Eveniment de cablu",
        "sim.option.hostile": "Inamic",
        "sim.option.friendly": "Aliat",
        "sim.option.neutral": "Neutru"
    },
    "hu": {
        "header.badge.disconnected": "Kapcsolat nélküli",
        "header.threat": "Kockázat",
        "scenario.baltic": "Balti Habarcs",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Mediterrán",
        "btn.start": "Kezdés",
        "btn.stop": "Leállítás",
        "subheader.what": "Mit ez:",
        "subheader.what.text": "egy élő döntéshozatali támogatási környezet, amely szintézis kontaktokat fogad be, frissíti a kockázati állapotot, generál konzultációs COA-kat, szimulál eredményeket és ajánl egy csomagot.",
        "guide.step1": "1. Szcenárió kiválasztása",
        "guide.step2": "2. Indítás megnyomása",
        "guide.step3": "3. Figyelje meg, hogyan változnak a kontaktok és a kockázat",
        "guide.step4": "4. COA/csomag áttekintése",
        "guide.step5": "5. Használja a Szimulátort egységek beviteléséhez vagy szerkesztéséhez",
        "guide.step6": "6. Briefing generálása",
        "why.changed": "Mit változott",
        "map.style": "Térkép stílus",
        "map.style.osm_standard": "Standard OSM",
        "map.style.osm_humanitarian": "OSM humanitárius",
        "map.style.carto_light": "Carto világos",
        "map.style.carto_dark": "Carto sötét",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Egységek szűrése",
        "map.filter.friendly": "Szövetségesek",
        "map.filter.hostile": "Ellenségesek",
        "map.filter.neutral": "Semlegesek",
        "map.filter.air": "Pszter",
        "map.filter.naval": "Tengeri",
        "map.filter.land": "Kontinentális",
        "map.filter.infra": "Infrastruktúra",
        "map.filter.cable_routes": "Kábelútvonalak megjelenítése",
        "map.filter.noaa_traffic": "NOAA forgalom lejátszása",
        "tab.guide": "Útmutató",
        "tab.contacts": "Kontaktok",
        "tab.coas": "COA-k",
        "tab.briefing": "Briefing",
        "tab.simulator": "Szimulátor",
        "tab.log": "Napló",
        "guide.how_title": "Hogyan működik a rendszer",
        "guide.how.1": "A motor kiüti vagy fogad kontaktokat, mint hajókat, UAV-kat, interferencia jelentéseket és kábeles eseményeket.",
        "guide.how.2": "Minden új kontakt frissíti az élő állapotot és a kontaktok előzményeit.",
        "guide.how.3": "Az elemzési ciklus újra kiszámítja az anomália indikátorokat és a kockázati valószínűségeket az entitásごとに.",
        "guide.how.4": "A COA motor szabályok alapján generál opciókat. Nem engedi meg az LLM-nek, hogy kitaláljon akciókat.",
        "guide.how.5": "Minden COA szimulálásra és pontozásra kerül. Ezután az assigner ellenőrzi, hogy egy koordinált COA csomag valóban megvalósítható-e a jelenlegi erőforrásokkal.",
        "guide.how.6": "A rendszer kiemeli a legjobb ajánlást, és igény szerint generálhat parancsnoki stílusú briefinget.",
        "guide.control_title": "Mit irányít",
        "guide.control.1": "<b>Szenárió:</b> válaszd ki a szintézis operációs területet és a szcenáriós kockázatfejlődést.",
        "guide.control.2": "<b>Indítás / Leállítás:</b> indítja vagy leállítja az élő tick ciklust.",
        "guide.control.3": "<b>Térkép:</b> a bal oldal mindig megmutatja a kontaktok aktuális képét.",
        "guide.control.4": "<b>NOAA Forgalom Lejátszása:</b> opcionális réteg NOAA historikus AIS nyomkövetései, amelyek a szcenárióban helyezkednek el demo viselkedéshez.",
        "guide.control.5": "<b>Szimulátor:</b> bevitel, szerkesztés, törlés vagy szcenáriós kezelés egységeknek.",
        "guide.control.6": "<b>Briefing:</b> generál egy könnyen olvasható magyarázatot az aktuális ajánlásról.",
        "guide.steps_title": "Lépésről lépésre",
        "guide.steps.1": "Nyisd meg ezt a dashboardot és válaszd ki egy szcenáriót a felső sávból.",
        "guide.steps.2": "Nyomd meg az <b>Indítás</b>. A motor elkezdi haladni, és a helyzet fejlődik.",
        "guide.steps.3": "Figyelj a bal oldali térképen és a felső sávban lévő <b>Kockázat</b> indikátoron. Ha magasra vagy kritikusra ugrál, az elemzés releváns változást észlel. ",
        "guide.steps.4": "Nyisd meg a <b>Kontaktok</b> részt, hogy láss pontos egységeket és figyelmeztetési zászlókat.",
        "guide.steps.5": "Nyisd meg a <b>COA-k</b> részt, hogy áttekintsd a besorolt opciókat. Ha létezik koordinált csomag, az a 개별 COA-k felett jelenik meg.",
        "guide.steps.6": "Nyisd meg a <b>Szimulátor</b> részt, ha új egységet akarsz elhelyezni a térképen, vagy erőltetni manővert, interferenciát vagy megközelítést.",
        "guide.steps.7": "Nyomd meg az <b>Briefing generálása</b>, amikor egy tömör operációs összefoglalót szeretnél.",
        "guide.callout.major_change": "Mit számít jelent jelentős változás?",
        "guide.callout.major_change.text": "Példák: egy hajó infrastruktúrához fordul, körbejár egy kábel közelében, egy UAV megjelenik az repülőtér közelében, interferencia kerül ki, vagy megváltozik az ajánlott COA.",
        "guide.callout.bundle_q": "Mi az a csomag?",
        "guide.callout.bundle_a": "Egy csomag egyszerűen több konzultációs COA, amelyek együtt értelmesek, például árnyékolás + ISR + kábelvédelem. Ez nem különálló vagy titokzatos mód.",
        "guide.callout.not_doing": "Amit a rendszer nem tesz:",
        "guide.callout.not_doing.text": "nem végrehajt parancsokat, nem oszt meg fegyvereket és nem engedi meg autonóm független konfrontációkat.",
        "contacts.stat.contacts": "Kontaktok",
        "contacts.stat.tracks": "Nyomkövetések",
        "contacts.stat.coas": "COA-k",
        "contacts.stat.processed": "Elmunkált",
        "briefing.generate": "Briefing generálás",
        "briefing.download_pdf": "PDF letöltése",
        "briefing.download_pdf_en": "PDF letöltése (EN)",
        "sim.quick_scenarios": "Gyors szcenáriók",
        "sim.quick_desc": "Használja ezeket a beállításokat, ha szeretné, hogy a motor láthatóan reagáljon. Az ellenséges és ismeretlen kontaktok növelik a nyomást. A szövetséges patroll és ISR javítja a rendelkezésre álló támogatást, és megnyithat erősebb koordinált csomagokat.",
        "sim.play.maritime_threat": "Tengeri kockázat a kábel közelében",
        "sim.play.maritime_threat.desc": "Bevitel egy ellenséges hajóval a kábel közelében, kikapcsolt AIS-szel és gyanús alacsony sebességű viselkedéssel",
        "sim.play.uav_airport": "UAV az repülőtér közelében",
        "sim.play.uav_airport.desc": "Bevitel egy ellenséges UAV-val légtér kockázati jelzettel",
        "sim.play.ew_escalation": "EW eskaláció",
        "sim.play.ew_escalation.desc": "Bevitel egy interferencia forrással az aktuális operációs területen",
        "sim.play.allied_isr": "Szövetséges ISR támogatás hozzáadása",
        "sim.play.allied_isr.desc": "Bevitel egy baráti UAV/támogató aktívum a pozícióváltás teszteléséhez",
        "sim.play.allied_patrol": "Szövetséges patroll hozzáadása",
        "sim.play.allied_patrol.desc": "Bevitel egy szövetséges patrollhajóval a zónában",
        "sim.play.cable_alert": "Infrastruktúra esemény",
        "sim.play.cable_alert.desc": "Bevitel egy kábeles esemény jelzettel a térkép közepén",
        "sim.undo_last": "Utolsó bevitelés visszavonása",
        "sim.reset_scenario": "Szenárió visszaállítása",
        "sim.preset.suspicious_vessel": "Gyanús hajó",
        "sim.preset.suspicious_vessel.desc": "Ellenséges hajó a térkép aktuális közepén",
        "sim.preset.hostile_uav": "Ellenséges UAV",
        "sim.preset.hostile_uav.desc": "Magas kockázati jelzettel rendelkező UAV",
        "sim.preset.jamming_event": "Interferencia esemény",
        "sim.preset.jamming_event.desc": "Bevitel egy interferencia kontaktussal, amely befolyásolja az anomáliákat",
        "sim.preset.cable_event": "Kábeles esemény",
        "sim.preset.cable_event.desc": "Bevitel egy kábelvágás típusú eseményjelzettel",
        "sim.quick.add_suspicious": "Most gyanús hajó hozzáadása",
        "sim.quick.add_suspicious.desc": "azonnali ellenséges tengeri kontakt a térkép közepén",
        "sim.quick.add_uav": "Most ellenséges UAV hozzáadása",
        "sim.quick.add_uav.desc": "azonnali légbeli kontakt az aktuális zóna közelében",
        "sim.quick.trigger_jamming": "Most interferencia aktiválása",
        "sim.quick.trigger_jamming.desc": "azonnali EW típusú anomália az aktuális zónában",
        "sim.quick.trigger_cable": "Most kábel figyelmeztetés aktiválása",
        "sim.quick.trigger_cable.desc": "azonnali infrastruktúra esemény a térkép közepén",
        "sim.show_advanced": "Részletes elhelyezés megjelenítése",
        "sim.form.name": "Név",
        "sim.form.type": "Típus",
        "sim.form.allegiance": "Szövetség",
        "sim.form.speed": "Sebesség (kts)",
        "sim.form.heading": "Irány",
        "sim.form.latitude": "Émagasság",
        "sim.form.longitude": "Magasság",
        "sim.form.jamming_radius": "Interferencia sugár (mn)",
        "sim.form.ais_off": "AIS kikapcsolt",
        "sim.form.position": "Pozíció",
        "sim.form.add_unit": "Egység hozzáadása",
        "sim.form.cancel": "Mégse",
        "sim.option.vessel": "Hajó",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Alsóvízi",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferencia",
        "sim.option.cable_event": "Kábeles esemény",
        "sim.option.hostile": "Ellenséges",
        "sim.option.friendly": "Szövetséges",
        "sim.option.neutral": "Semleges"
    },
    "bg": {
        "header.badge.disconnected": "Разкъснат",
        "header.threat": "Заплаха",
        "scenario.baltic": "Балтийско море",
        "scenario.arctic": "Арктика",
        "scenario.mediterranean": "Средиземно море",
        "btn.start": "Стартирай",
        "btn.stop": "Спитай",
        "subheader.what": "Какво е това:",
        "subheader.what.text": "жива среда за подпомагане на вземане на решения, която приема синтетични контакти, актуализира състоянието на заплаха, генерира консултативни COA, симулира резултати и препоръчва пакет.",
        "guide.step1": "1. Изберете сценарий",
        "guide.step2": "2. Натиснете Стартирай",
        "guide.step3": "3. Наблюдавайте как се променят контактите и заплахата",
        "guide.step4": "4. Прегледайте COA / пакет",
        "guide.step5": "5. Използвайте Симулатора, за да инжектирате или редактирате единици",
        "guide.step6": "6. Генерирайте брифинг",
        "why.changed": "Какво се промени",
        "map.style": "Стил на картата",
        "map.style.osm_standard": "Стандартен OpenStreetMap",
        "map.style.osm_humanitarian": "Хуманитарен OSM",
        "map.style.carto_light": "Светла Carto",
        "map.style.carto_dark": "Тъмна Carto",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Филтриране на единиците",
        "map.filter.friendly": "Съюзници",
        "map.filter.hostile": "Врагове",
        "map.filter.neutral": "Неутрални",
        "map.filter.air": "Въздушни",
        "map.filter.naval": "Морски",
        "map.filter.land": "Наземни",
        "map.filter.infra": "Инфраструктура",
        "map.filter.cable_routes": "Показване на кабелни маршрути",
        "map.filter.noaa_traffic": "Показване на NOAA трафик запис",
        "tab.guide": "Ръководство",
        "tab.contacts": "Контакти",
        "tab.coas": "COA",
        "tab.briefing": "Брифинг",
        "tab.simulator": "Симулатор",
        "tab.log": "Журнал",
        "guide.how_title": "Как работи системата",
        "guide.how.1": "Двигателят излъчва или получава контакти като кораби, UAV, доклади за интерференция и кабелни събития.",
        "guide.how.2": "Всеки нов контакт актуализира животото състояние и историята на контактите.",
        "guide.how.3": "Цикълът на анализ преизчислява индикатори за аномалии и вероятности за заплаха на единица.",
        "guide.how.4": "Двигателят на COA генерира опции въз основа на правила. Не позволява на LLM да измисля действия.",
        "guide.how.5": "Всеки COA се симулира и оценява. След това назначаващият проверява дали координиран пакет от няколко COA е наистина жизнеспособен с наличните средства.",
        "guide.how.6": "Системата подчертава най-доброто препоръчано решение и може да генерира брифинг в стил на командир по заявка.",
        "guide.control_title": "Какво контролирате",
        "guide.control.1": "<b>Сценарий:</b> избирате синтетичната оперативна зона и сценаризираната еволюция на заплахата.",
        "guide.control.2": "<b>Стартирай / Спитай:</b> стартира или спира цикъла на животото 'ticks'.",
        "guide.control.3": "<b>Карта:</b> лявата страна винаги показва текущото изображение на контактите.",
        "guide.control.4": "<b>NOAA Replay Трафик:</b> опционален слой с исторически AIS трасери от NOAA, преместени в сценария за демонстрационно поведение.",
        "guide.control.5": "<b>Симулатор:</b> инжектира, редактира, изтрива или сценаризира поведението на единиците.",
        "guide.control.6": "<b>Брифинг:</b> генерира разбираемо обяснение на текущата препоръка.",
        "guide.steps_title": "Стъпка по стъпка",
        "guide.steps.1": "Отворете този дашборд и изберете сценарий в горната лента.",
        "guide.steps.2": "Натиснете <b>Стартирай</b>. Двигателят започва да напредва и ситуацията се развива.",
        "guide.steps.3": "Наблюдавайте картата отляво и индикатора за <b>Заплаха</b> в заглавието. Ако скочи на ВИСОКА или КРИТИЧНА, анализът е открил значителна промяна.",
        "guide.steps.4": "Отворете <b>Контакти</b>, за да видите активни единици и сигнали за тревога.",
        "guide.steps.5": "Отворете <b>COA</b>, за да прегледате класифицираните опции. Ако има координиран пакет, той се появява над отделните COA.",
        "guide.steps.6": "Отворете <b>Симулатор</b>, ако искате да поставите нова единица на картата или да принудите маневра, интерференция или приближаване.",
        "guide.steps.7": "Натиснете <b>Генерирайте брифинг</b>, когато искате кратко оперативна обобщение.",
        "guide.callout.major_change": "Какво се счита за значителна промяна?",
        "guide.callout.major_change.text": "Примери: кораб се обръща към инфраструктура, патрулира близо до кабел, се появява UAV близо до летището, се излъчва интерференция или се променя препоръчаната COA.",
        "guide.callout.bundle_q": "Какво е пакет?",
        "guide.callout.bundle_a": "Пакетът е просто няколко консултативни COA, които имат смисъл заедно, например сенки + ISR + защита на кабела. Не е отделен или мистериозен режим.",
        "guide.callout.not_doing": "Какво не прави системата:",
        "guide.callout.not_doing.text": "не изпълнява команди, не назначава оръжия и не разрешава бой автономно.",
        "contacts.stat.contacts": "Контакти",
        "contacts.stat.tracks": "Трасери",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Обработени",
        "briefing.generate": "Генериране на брифинг",
        "briefing.download_pdf": "Изтегляне на PDF",
        "briefing.download_pdf_en": "Изтегляне на PDF (EN)",
        "sim.quick_scenarios": "Бързи сценарии",
        "sim.quick_desc": "Използвайте тези предварителни настройки, ако искате двигателят да реагира видимо. Враговите и неизвестните контакти повишават напрежението. Съюзни патрули и ISR подобряват наличното подпомагане и могат да отключат по-силни координирани пакети.",
        "sim.play.maritime_threat": "Морска заплаха близо до кабела",
        "sim.play.maritime_threat.desc": "Инжектира вражески кораб близо до инфраструктура с изключен AIS и подозрително поведение при ниска скорост",
        "sim.play.uav_airport": "UAV близо до летището",
        "sim.play.uav_airport.desc": "Инжектира вражески UAV със сигнал за риск от въздушно пространство",
        "sim.play.ew_escalation": "Ескалация на EW",
        "sim.play.ew_escalation.desc": "Инжектира източник на интерференция в текущата оперативна зона",
        "sim.play.allied_isr": "Добавяне на съюзни ISR подпомоги",
        "sim.play.allied_isr.desc": "Инжектира приятелски UAV/активен подкрепящ елемент за тестване на промени в позицията",
        "sim.play.allied_patrol": "Добавяне на съюзни патрули",
        "sim.play.allied_patrol.desc": "Инжектира съюзски патрулен кораб в зоната",
        "sim.play.cable_alert": "Инцидент с инфраструктура",
        "sim.play.cable_alert.desc": "Инжектира сигнал за кабелно събитие близо до центъра на картата",
        "sim.undo_last": "Отмени последната инжекция",
        "sim.reset_scenario": "Презареди сценария",
        "sim.preset.suspicious_vessel": "Подозрителен кораб",
        "sim.preset.suspicious_vessel.desc": "Вражески кораб близо до текущия център на картата",
        "sim.preset.hostile_uav": "Враждебен UAV",
        "sim.preset.hostile_uav.desc": "UAV със повишен сигнал за заплаха",
        "sim.preset.jamming_event": "Интерференционно събитие",
        "sim.preset.jamming_event.desc": "Инжектира контакт за интерференция, който засяга аномалиите",
        "sim.preset.cable_event": "Кабелно събитие",
        "sim.preset.cable_event.desc": "Инжектира събитие от типа прекъсване на кабел",
        "sim.quick.add_suspicious": "Добави подозрителен кораб сега",
        "sim.quick.add_suspicious.desc": "Незабавен вражески морски контакт в центъра на картата",
        "sim.quick.add_uav": "Добави враждебен UAV сега",
        "sim.quick.add_uav.desc": "Незабавен въздушен контакт близо до текущата зона",
        "sim.quick.trigger_jamming": "Активирай интерференция сега",
        "sim.quick.trigger_jamming.desc": "Незабавна EW аномалия в текущата зона",
        "sim.quick.trigger_cable": "Активирай кабелна тревога сега",
        "sim.quick.trigger_cable.desc": "Незабавен инцидент с инфраструктура близо до центъра на картата",
        "sim.show_advanced": "Покажи разширено позициониране",
        "sim.form.name": "Име",
        "sim.form.type": "Тип",
        "sim.form.allegiance": "Принадлежност",
        "sim.form.speed": "Скорост (kts)",
        "sim.form.heading": "Курс",
        "sim.form.latitude": "Ширина",
        "sim.form.longitude": "Дължина",
        "sim.form.jamming_radius": "Радиус на интерференция (mn)",
        "sim.form.ais_off": "AIS изключен",
        "sim.form.position": "Позиция",
        "sim.form.add_unit": "Добави единица",
        "sim.form.cancel": "Откажи",
        "sim.option.vessel": "Кораб",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Подводна лодка",
        "sim.option.convoy": "Конвой",
        "sim.option.jamming": "Интерференция",
        "sim.option.cable_event": "Кабелно събитие",
        "sim.option.hostile": "Враждебен",
        "sim.option.friendly": "Съюзник",
        "sim.option.neutral": "Неутрален"
    },
    "hr": {
        "header.badge.disconnected": "Odvojen",
        "header.threat": "Prijetnja",
        "scenario.baltic": "Baltičko more",
        "scenario.arctic": "Arktik",
        "scenario.mediterranean": "Sredozemno more",
        "btn.start": "Pokreni",
        "btn.stop": "Zaustavi",
        "subheader.what": "Što je ovo:",
        "subheader.what.text": "živo okruženje za donošenje odluka koje prima sintetičke kontakte, ažurira status prijetnje, generira konsultativne COA-e, simulira rezultate i preporučuje paket.",
        "guide.step1": "1. Odaberi scenarij",
        "guide.step2": "2. Pritisni Pokreni",
        "guide.step3": "3. Promatraj kako se kontakti i prijetnja mijenjaju",
        "guide.step4": "4. Pregledaj COA / paket",
        "guide.step5": "5. Koristi Simulator za injektiranje ili uređivanje jedinica",
        "guide.step6": "6. Generiraj brifing",
        "why.changed": "Što se promijenilo",
        "map.style": "Stil mape",
        "map.style.osm_standard": "Standardni OSM",
        "map.style.osm_humanitarian": "Humanitarni OSM",
        "map.style.carto_light": "Carto svijetlo",
        "map.style.carto_dark": "Carto tamno",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtriraj jedinice",
        "map.filter.friendly": "Prijateljski",
        "map.filter.hostile": "Neprijateljski",
        "map.filter.neutral": "Neutralni",
        "map.filter.air": "Zračni",
        "map.filter.naval": "Morski",
        "map.filter.land": "Nzemaljski",
        "map.filter.infra": "Infrastruktura",
        "map.filter.cable_routes": "Prikaži kabelske rute",
        "map.filter.noaa_traffic": "Prikaži NOAA replay prometa",
        "tab.guide": "Vodič",
        "tab.contacts": "Kontakti",
        "tab.coas": "COA-e",
        "tab.briefing": "Brifing",
        "tab.simulator": "Simulator",
        "tab.log": "Log",
        "guide.how_title": "Kako sustav funkcionira",
        "guide.how.1": "Motor emitira ili prima kontakte kao brodove, UAV-ove, izvještaje o smetnjama i događaje s kablovima.",
        "guide.how.2": "Svaki novi kontakt ažurira živi status i povijest kontakata.",
        "guide.how.3": "Ciklus analize ponovno izračunava indikatore anomalije i vjerojatnosti prijetnje po entitetu.",
        "guide.how.4": "COA motor generira opcije na temelju pravila. Ne dopušta LLM-u da izmišlja akcije.",
        "guide.how.5": "Svaki COA se simulira i ocjenjuje. Nakon toga dodjeljivač provjerava je li koordinirani paket više COA-a zaista izvodljiv s trenutnim sredstvima.",
        "guide.how.6": "Sustav ističe najbolju preporuku i može generirati brifing tipa komandanta po potrebi.",
        "guide.control_title": "Što kontrolirate",
        "guide.control.1": "<b>Scenarij:</b> odaberi sintetičku operativnu zonu i scenarijiziranu evoluciju prijetnje.",
        "guide.control.2": "<b>Pokreni / Zaustavi:</b> pokreće ili zaustavlja ciklus živog tik-a.",
        "guide.control.3": "<b>Mapa:</b> lijeva strana uvijek prikazuje trenutni prikaz kontakata.",
        "guide.control.4": "<b>NOAA Replay Prometa:</b> opcionalni sloj povijesnih AIS trajektorija NOAA premeštenih u scenarij za demo ponašanje.",
        "guide.control.5": "<b>Simulator:</b> injektira, uređuje, briše ili scenarijizira ponašanje jedinica.",
        "guide.control.6": "<b>Brifing:</b> generira čitljiv objašnjenje trenutne preporuke.",
        "guide.steps_title": "Korak po korak",
        "guide.steps.1": "Otvorite ovaj dashboard i odaberite scenarij u gornjoj traci.",
        "guide.steps.2": "Pritisnite <b>Pokreni</b>. Motor počinje napredovati i situacija evoluira.",
        "guide.steps.3": "Promatrajte mapu lijevo i indikator <b>Prijetnja</b> u zaglavlju. Ako se preskoči na VISOKU ili KRITIČNU, analiza je detektirala relevantnu promjenu.",
        "guide.steps.4": "Otvorite <b>Kontakti</b> kako biste vidjeli aktivne jedinice i alarme.",
        "guide.steps.5": "Otvorite <b>COA-e</b> kako biste pregledali klasificirane opcije. Ako postoji koordinirani paket, pojavljuje se iznad pojedinačnih COA-a.",
        "guide.steps.6": "Otvorite <b>Simulator</b> ako želite postaviti novu jedinicu na mapu ili prisiliti manevar, smetnju ili približavanje.",
        "guide.steps.7": "Pritisnite <b>Generiraj brifing</b> kada želite sažetak operacija.",
        "guide.callout.major_change": "Što se smatra značajnom promjenom?",
        "guide.callout.major_change.text": "Primjeri: brod okreće prema infrastrukturi, kruži blizu kabla, pojavljuje se UAV blizu zračne luke, emitira se smetnja ili se mijenja preporučena COA.",
        "guide.callout.bundle_q": "Što je paket?",
        "guide.callout.bundle_a": "Paket je jednostavno više konsultativnih COA-a koje imaju smisla zajedno, npr. sjena + ISR + zaštita kabla. Nije odvojeni niti misteriozni način.",
        "guide.callout.not_doing": "Što sustav ne radi:",
        "guide.callout.not_doing.text": "ne izvršava naredbe, ne dodjeljuje oružje i ne autorizira sukobe autonomno.",
        "contacts.stat.contacts": "Kontakti",
        "contacts.stat.tracks": "Trajektore",
        "contacts.stat.coas": "COA-e",
        "contacts.stat.processed": "Obrađeno",
        "briefing.generate": "Generiraj brifing",
        "briefing.download_pdf": "Preuzmi PDF",
        "briefing.download_pdf_en": "Preuzmi PDF (EN)",
        "sim.quick_scenarios": "Brzi scenariji",
        "sim.quick_desc": "Koristite ove predloške ako želite da motor reagira vidljivo. Neprijateljski i nepoznati kontakti povećavaju pritisak. Prijateljska patrola i ISR poboljšavaju dostupnu podršku i mogu otključati jače koordinirane pakete.",
        "sim.play.maritime_threat": "Morska prijetnja blizu kabla",
        "sim.play.maritime_threat.desc": "Injektira neprijateljski brod blizu infrastrukture s isključenim AIS-om i sumnjivim ponašanjem niskom brzinom",
        "sim.play.uav_airport": "UAV blizu zračne luke",
        "sim.play.uav_airport.desc": "Injektira neprijateljski UAV s potpisom rizika u zračnom prostoru",
        "sim.play.ew_escalation": "EW Eskalacija",
        "sim.play.ew_escalation.desc": "Injektira izvor smetnje u trenutnoj operativnoj zoni",
        "sim.play.allied_isr": "Dodaj prijateljski ISR",
        "sim.play.allied_isr.desc": "Injektira prijateljski UAV/aktiv za podršku za testiranje promjena stava",
        "sim.play.allied_patrol": "Dodaj prijateljsku patrolu",
        "sim.play.allied_patrol.desc": "Injektira prijateljski patrolni brod u zonu",
        "sim.play.cable_alert": "Infrastrukturni incident",
        "sim.play.cable_alert.desc": "Injektira alarm tipa događaja s kablom blizu središta mape",
        "sim.undo_last": "Poništi zadnju injekciju",
        "sim.reset_scenario": "Resetiraj scenarij",
        "sim.preset.suspicious_vessel": "Sumnjivi brod",
        "sim.preset.suspicious_vessel.desc": "Neprijateljski brod blizu trenutnog središta mape",
        "sim.preset.hostile_uav": "Neprijateljski UAV",
        "sim.preset.hostile_uav.desc": "UAV s povišenim potpisom prijetnje",
        "sim.preset.jamming_event": "Događaj smetnje",
        "sim.preset.jamming_event.desc": "Injektira kontakt smetnje koji utječe na anomalije",
        "sim.preset.cable_event": "Događaj s kablom",
        "sim.preset.cable_event.desc": "Injektira događaj tipa kidanje kabla",
        "sim.quick.add_suspicious": "Dodaj sumnjivi brod sada",
        "sim.quick.add_suspicious.desc": "Odmah neprijateljski morski kontakt u središtu mape",
        "sim.quick.add_uav": "Dodaj neprijateljski UAV sada",
        "sim.quick.add_uav.desc": "Odmah zračni kontakt blizu trenutne zone",
        "sim.quick.trigger_jamming": "Aktiviraj smetnju sada",
        "sim.quick.trigger_jamming.desc": "Odmah anomalija tipa EW u trenutnoj zoni",
        "sim.quick.trigger_cable": "Aktiviraj alarm kabla sada",
        "sim.quick.trigger_cable.desc": "Odmah infrastrukturalni incident blizu središta mape",
        "sim.show_advanced": "Prikaži napredno postavljanje",
        "sim.form.name": "Naziv",
        "sim.form.type": "Tip",
        "sim.form.allegiance": "Pripadnost",
        "sim.form.speed": "Brzina (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Latituda",
        "sim.form.longitude": "Longituda",
        "sim.form.jamming_radius": "Poluprečnik smetnje (mn)",
        "sim.form.ais_off": "AIS isključen",
        "sim.form.position": "Pozicija",
        "sim.form.add_unit": "Dodaj jedinicu",
        "sim.form.cancel": "Odustani",
        "sim.option.vessel": "Brod",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Podmorski",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Smetnja",
        "sim.option.cable_event": "Događaj s kablom",
        "sim.option.hostile": "Neprijateljski",
        "sim.option.friendly": "Prijateljski",
        "sim.option.neutral": "Neutralni"
    },
    "sk": {
        "header.badge.disconnected": "Odpojené",
        "header.threat": "Hrozba",
        "scenario.baltic": "Baltický mor",
        "scenario.arctic": "Arktikum",
        "scenario.mediterranean": "Meditské more",
        "btn.start": "Začať",
        "btn.stop": "Zastaviť",
        "subheader.what": "Čo je to:",
        "subheader.what.text": "živé prostredie pre podklad rozhodovania, ktoré prijíma syntetické kontakty, aktualizuje stav hrozby, generuje konzultívne COA, simuluje výsledky a odporúča balík.",
        "guide.step1": "1. Vybrať scenár",
        "guide.step2": "2. Kliknúť Začať",
        "guide.step3": "3. Pozorovať zmenu kontaktov a hrozby",
        "guide.step4": "4. Prehliadať COA / balík",
        "guide.step5": "5. Použiť Simulátor na injekciu alebo editáciu jednotiek",
        "guide.step6": "6. Vygenerovať briefing",
        "why.changed": "Čo sa zmenilo",
        "map.style": "Styl mapy",
        "map.style.osm_standard": "OSM štandard",
        "map.style.osm_humanitarian": "OSM humanitárny",
        "map.style.carto_light": "Carto svetlý",
        "map.style.carto_dark": "Carto tmavý",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrovať jednotky",
        "map.filter.friendly": "Priatelia",
        "map.filter.hostile": "Nepriatelia",
        "map.filter.neutral": "Neutrálna",
        "map.filter.air": "Vzdušné",
        "map.filter.naval": "Morské",
        "map.filter.land": "Pozemné",
        "map.filter.infra": "Infrastruktúra",
        "map.filter.cable_routes": "Zobraziť kábelové trasy",
        "map.filter.noaa_traffic": "Zobraziť NOAA replay tráfiku",
        "tab.guide": "Sprievodca",
        "tab.contacts": "Kontakty",
        "tab.coas": "COA",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulátor",
        "tab.log": "Kniha záznamov",
        "guide.how_title": "Ako funguje systém",
        "guide.how.1": "Motor vysiela alebo prijíma kontakty ako lodie, UAV, hlásenia interferencie a kábelové udalosti.",
        "guide.how.2": "Každý nový kontakt aktualizuje stav v reálnom čase a históriu kontaktov.",
        "guide.how.3": "Analytický cyklus prepočítava ukazovatele anomálií a pravdepodobnosti hrozby na entitu.",
        "guide.how.4": "Motor COA generuje možnosti na základe pravidiel. Neumožňuje LLM vymýšľať akcie.",
        "guide.how.5": "Každé COA sa simuluje a hodnotí. Následne kontroluje asignátor, či je koordinovaný balík niekoľkých COA skutočne realizovateľný s aktuálnymi prostriedkami.",
        "guide.how.6": "Systém zvýrazňuje najlepší odporúčanie a môže vygenerovať briefing štýlu veliteľa na požiadanie.",
        "guide.control_title": "Čo kontrolujete",
        "guide.control.1": "<b>Scenár:</b> vyberte syntetické operačné územie a scénarizovanú evolúciu hrozby.",
        "guide.control.2": "<b>Začať / Zastaviť:</b> začína alebo zastavuje cyklus živých tickov.",
        "guide.control.3": "<b>Mapa:</b> ľavá strana vždy zobrazuje aktuálny obraz kontaktov.",
        "guide.control.4": "<b>NOAA Tráfico Replay:</b> voliteľná vrstva historických AIS sledov NOAA presmerovaných do scenára pre demonstračné správanie.",
        "guide.control.5": "<b>Simulátor:</b> injektuje, edituje, odstraňuje alebo scénarizuje správanie jednotiek.",
        "guide.control.6": "<b>Briefing:</b> generuje čitateľný popis aktuálneho odporúčania.",
        "guide.steps_title": "Krok za krokom",
        "guide.steps.1": "Otvorte tento dashboard a vyberte scenár v hornom lište.",
        "guide.steps.2": "Kliknite na <b>Začať</b>. Motor začne postupovať a situácia sa vyvíja.",
        "guide.steps.3": "Pozorujte mapu vľavo a indikátor <b>Hrozba</b> v hlavičke. Ak sa zvýši na VYSOKÁ alebo KRÍTICKÁ, analýza detekovala relevantnú zmenu.",
        "guide.steps.4": "Otvorte <b>Kontakty</b> na zobrazenie aktívnych jednotiek a varovných signálov.",
        "guide.steps.5": "Otvorte <b>COA</b> na prehliadanie klasifikovaných možností. Ak existuje koordinovaný balík, zobrazí sa nad jednotlivými COA.",
        "guide.steps.6": "Otvorte <b>Simulátor</b>, ak chcete pridať novú jednotku na mapu alebo vynútiť manévru, interferenciu alebo približenie.",
        "guide.steps.7": "Kliknite na <b>Vygenerovať briefing</b>, keď chcete stručné operačné zhrnutie.",
        "guide.callout.major_change": "Čo sa považuje za významnú zmenu?",
        "guide.callout.major_change.text": "Príklady: loď smeruje k infraštruktúre, krúži blízko kábla, objaví sa UAV blízko letiska, vysiela sa interferencia alebo sa zmení odporúčaná COA.",
        "guide.callout.bundle_q": "Čo je balík?",
        "guide.callout.bundle_a": "Balík je jednoducho niekoľko konzultatívnych COA, ktoré majú zmysel spolu, napríklad cieň + ISR + ochrana kábla. Nie je to samostatný ani tajomný režim.",
        "guide.callout.not_doing": "Čo systém nerobí:",
        "guide.callout.not_doing.text": "nevykonáva rozkazy, nepresudzuje zbrane a neautorizuje bojové akcie autonomne.",
        "contacts.stat.contacts": "Kontakty",
        "contacts.stat.tracks": "Sledy",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Zpracované",
        "briefing.generate": "Vygenerovať briefing",
        "briefing.download_pdf": "Stiahnuť PDF",
        "briefing.download_pdf_en": "Stiahnuť PDF (EN)",
        "sim.quick_scenarios": "Rýchle scenárie",
        "sim.quick_desc": "Použite tieto prednastavenia, ak chcete, aby motor reagoval viditeľne. Nepriateľské a neznáme kontakty zvyšujú tlak. Priateľská patrola a ISR zlepšujú dostupnú podporu a môžu odblokovať silnejšie koordinované balíky.",
        "sim.play.maritime_threat": "Morské hrozby blízko kábla",
        "sim.play.maritime_threat.desc": "Injektuje nepriateľskú loď blízko infraštruktúry s vypnutým AIS a podozrivým správaním pri nízkej rýchlosti",
        "sim.play.uav_airport": "UAV blízko letiska",
        "sim.play.uav_airport.desc": "Injektuje nepriateľské UAV s signálom rizika pre vzdušný priestor",
        "sim.play.ew_escalation": "ES eskalácia",
        "sim.play.ew_escalation.desc": "Injektuje zdroj interferencie do aktuálneho operačného územia",
        "sim.play.allied_isr": "Pridať priateľskú podporu ISR",
        "sim.play.allied_isr.desc": "Injektuje priateľské UAV/aktívum podpory na testovanie zmeny postojov",
        "sim.play.allied_patrol": "Pridať priateľskú patrolu",
        "sim.play.allied_patrol.desc": "Injektuje priateľskú patrolnú loď do zóny",
        "sim.play.cable_alert": "Inšidencia infraštruktúry",
        "sim.play.cable_alert.desc": "Injektuje varovanie typu kábelová udalosť blízko stredu mapy",
        "sim.undo_last": "Zrušiť poslednú injekciu",
        "sim.reset_scenario": "Resetovať scenár",
        "sim.preset.suspicious_vessel": "Podozrivá loď",
        "sim.preset.suspicious_vessel.desc": "Nepriateľská loď blízko aktuálneho stredu mapy",
        "sim.preset.hostile_uav": "Nepriateľské UAV",
        "sim.preset.hostile_uav.desc": "UAV s zvýšeným signálom hrozby",
        "sim.preset.jamming_event": "Interferenčná udalosť",
        "sim.preset.jamming_event.desc": "Injektuje kontakt interferencie, ktorý ovplyvňuje anomálie",
        "sim.preset.cable_event": "Kábelová udalosť",
        "sim.preset.cable_event.desc": "Injektuje udalosť typu roztrhnutie kábla",
        "sim.quick.add_suspicious": "Pridať podozrivú loď teraz",
        "sim.quick.add_suspicious.desc": "Okamžitý nepriateľský morsky kontakt v strede mapy",
        "sim.quick.add_uav": "Pridať nepriateľské UAV teraz",
        "sim.quick.add_uav.desc": "Okamžitý vzdušný kontakt blízko aktuálnej zóny",
        "sim.quick.trigger_jamming": "Aktivovať interferenciu teraz",
        "sim.quick.trigger_jamming.desc": "Okamžitá EW anomália v aktuálnej zóne",
        "sim.quick.trigger_cable": "Aktivovať kábelové varovanie teraz",
        "sim.quick.trigger_cable.desc": "Okamžitá infraštruktúrna udalosť blízko stredu mapy",
        "sim.show_advanced": "Zobraziť pokročilú polohu",
        "sim.form.name": "Názov",
        "sim.form.type": "Typ",
        "sim.form.allegiance": "Afiliácia",
        "sim.form.speed": "Rýchlosť (kts)",
        "sim.form.heading": "Rúm",
        "sim.form.latitude": "Latitudy",
        "sim.form.longitude": "Longitudy",
        "sim.form.jamming_radius": "Polomier interferencie (mn)",
        "sim.form.ais_off": "AIS vypnuté",
        "sim.form.position": "Pozícia",
        "sim.form.add_unit": "Pridať jednotku",
        "sim.form.cancel": "Zrušiť",
        "sim.option.vessel": "Loď",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Podvodnica",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferencia",
        "sim.option.cable_event": "Kábelová udalosť",
        "sim.option.hostile": "Nepriateľský",
        "sim.option.friendly": "Priateľský",
        "sim.option.neutral": "Neutrálny"
    },
    "sl": {
        "header.badge.disconnected": "Odprt",
        "header.threat": "Grožnja",
        "scenario.baltic": "Baltičko morje",
        "scenario.arctic": "Arktik",
        "scenario.mediterranean": "Sredozemlje",
        "btn.start": "Začni",
        "btn.stop": "Ustani",
        "subheader.what": "Kaj je to:",
        "subheader.what.text": "živo okolje za podporo odločanju, ki vname sintetične kontakte, aktualizira stanje grožnje, generira konsultativne COA, simulira rezultate in priporoči paket.",
        "guide.step1": "1. Izberi scenarij",
        "guide.step2": "2. Pritisni Začni",
        "guide.step3": "3. Prekliči, kako se spreminjajo kontakti in grožnja",
        "guide.step4": "4. Preveri COA / paket",
        "guide.step5": "5. Uporabi Simulator za injekcijo ali ureditev enot",
        "guide.step6": "6. Generiraj brskopis",
        "why.changed": "Kaj se je spremenilo",
        "map.style": "Stil zemlje",
        "map.style.osm_standard": "Standardni OSM",
        "map.style.osm_humanitarian": "Humanitarni OSM",
        "map.style.carto_light": "Carto svetlo",
        "map.style.carto_dark": "Carto tamno",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtriraj enote",
        "map.filter.friendly": "Zgonske",
        "map.filter.hostile": "Nevarnostne",
        "map.filter.neutral": "Nevtralne",
        "map.filter.air": "Zračni",
        "map.filter.naval": "Morski",
        "map.filter.land": "Kameniti",
        "map.filter.infra": "Infrastruktura",
        "map.filter.cable_routes": "Prikaži kabelske traske",
        "map.filter.noaa_traffic": "Prikaži NOAA prometni ponovno odtvoritev",
        "tab.guide": "Vodič",
        "tab.contacts": "Kontakti",
        "tab.coas": "COA",
        "tab.briefing": "Brskopis",
        "tab.simulator": "Simulator",
        "tab.log": "Zapisnik",
        "guide.how_title": "Kako deluje sistem",
        "guide.how.1": "Motor pošilja ali sprejema kontakte kot ladje, UAV, poročila o interferenci in kabelski dogodki.",
        "guide.how.2": "Vsak nov kontakt aktualizira stanje v realnem času in zgodovino kontaktov.",
        "guide.how.3": "Analitični ciklus ponovno izračuna indikatorje anomalij in verjetnost grožnje po entiteti.",
        "guide.how.4": "Motor COA generira možnosti na podlagi pravil. Ne dovoljuje LLM-u, da izmisli dejanja.",
        "guide.how.5": "Vsaka COA se simulira in ocenjuje. Nato preverja dodeljevalec, ali je koordiniran paket več COA resnično izvedljiv z trenutnimi sredstvi.",
        "guide.how.6": "Sistem poudarja najboljšo priporočilo in lahko na zahtevo generira brskopis tipa vodnik.",
        "guide.control_title": "Kaj kontroliraš",
        "guide.control.1": "<b>Scenarij:</b> izberi sintetično operativno območje in scenarijno evolucijo grožnje.",
        "guide.control.2": "<b>Začni / Ustani:</b> začne ali ustani ciklus v realnem času.",
        "guide.control.3": "<b>Mapa:</b> levi del vedno prikazuje trenutno sliko kontaktov.",
        "guide.control.4": "<b>NOAA Replay promet:</b> opcijska sloj zgodovinskih AIS sledi NOAA, premesjenih v scenarij za demo vedenje.",
        "guide.control.5": "<b>Simulator:</b> injicira, ureja, izbriše ali scenarijizira vedenje enot.",
        "guide.control.6": "<b>Brskopis:</b> generira berljiv opis trenutne priporočile.",
        "guide.steps_title": "Korak po korak",
        "guide.steps.1": "Otvori ta nadzorna ploča in izberi scenarij v zgornjem vrstici.",
        "guide.steps.2": "Pritisni <b>Začni</b>. Motor začne napredovati in se situacija razvija.",
        "guide.steps.3": "Prekliči mapo na levi in indikator <b>Grožnja</b> v glavi. Če se poveča na VISOKO ali KRITIČNO, je analiza obvestila o pomembenem spreminjanju.",
        "guide.steps.4": "Otvori <b>Kontakti</b>, da vidiš aktivne enote in varnostne zastave.",
        "guide.steps.5": "Otvori <b>COA</b>, da preveriš razvrščene možnosti. Če obstaja koordiniran paket, se pojavi nad posameznimi COA.",
        "guide.steps.6": "Otvori <b>Simulator</b>, če želiš postaviti novo enoto na mapo ali prisiliti manevr, interferenco ali približevanje.",
        "guide.steps.7": "Pritisni <b>Generiraj brskopis</b>, ko želiš koncizan operativni povzetek.",
        "guide.callout.major_change": "Kaj se šteje za pomembno spremembo?",
        "guide.callout.major_change.text": "Primeri: ladja se obrne k infrastrukturi, cirkulira blizu kabla, se pojavi UAV blizu letišča, se pošlje interferenca ali se spremeni priporočena COA.",
        "guide.callout.bundle_q": "Kaj je paket?",
        "guide.callout.bundle_a": "Paket je preprosto več konsultativnih COA, ki imajo smisel skupaj, na primer senčenje + ISR + zaščita kabla. Ni odločen način ali skrivnosten.",
        "guide.callout.not_doing": "Kaj sistem ne dela:",
        "guide.callout.not_doing.text": "ne izvršuje nalog, ne dodeljuje oružja in ne dovoljuje konfrontacij samostojno.",
        "contacts.stat.contacts": "Kontakti",
        "contacts.stat.tracks": "Sledi",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Obdelani",
        "briefing.generate": "Generiraj brskopis",
        "briefing.download_pdf": "Prenesi PDF",
        "briefing.download_pdf_en": "Prenesi PDF (EN)",
        "sim.quick_scenarios": "Hitri scenariji",
        "sim.quick_desc": "Uporabi te prednastavitve, če želiš, da motor reagira vidno. Nevarnostni in neznani kontakti povečajo pritisk. Patrulja in zgonski ISR izboljšajo dostopno podporo in lahko odbločejo močnejše koordinirane pakete.",
        "sim.play.maritime_threat": "Morska grožnja blizu kabla",
        "sim.play.maritime_threat.desc": "Injekcija nevarnosti ladje blizu infrastrukture z izklopljeno AIS in s sumljivim vedenjem nizke hitrosti",
        "sim.play.uav_airport": "UAV blizu letišča",
        "sim.play.uav_airport.desc": "Injekcija nevarnosti UAV z podpisom tveganja za zračni prostor",
        "sim.play.ew_escalation": "EW eskalacija",
        "sim.play.ew_escalation.desc": "Injekcija izvora interferenčnega vpliva v trenutno operativno območje",
        "sim.play.allied_isr": "Dodaj zgonski ISR podporo",
        "sim.play.allied_isr.desc": "Injekcija zgonskega UAV/podpore za testiranje sprememb držanja",
        "sim.play.allied_patrol": "Dodaj zgonsko patruljo",
        "sim.play.allied_patrol.desc": "Injekcija zgonske patruljne ladje v območje",
        "sim.play.cable_alert": "Dogodek z infrastrukturo",
        "sim.play.cable_alert.desc": "Injekcija alarma tipa kabelski dogodek blizu sredine mape",
        "sim.undo_last": "Zavrni zadnjo injekcijo",
        "sim.reset_scenario": "Ponastavi scenarij",
        "sim.preset.suspicious_vessel": "Sumljiva ladja",
        "sim.preset.suspicious_vessel.desc": "Nevarnostna ladja blizu trenutnega središča mape",
        "sim.preset.hostile_uav": "Nevarnostni UAV",
        "sim.preset.hostile_uav.desc": "UAV zviščenega tveganja grožnje",
        "sim.preset.jamming_event": "Dogodek interferenčnega vpliva",
        "sim.preset.jamming_event.desc": "Injekcija kontakta interferenčnega vpliva, ki vpliva na anomalije",
        "sim.preset.cable_event": "Kabelski dogodek",
        "sim.preset.cable_event.desc": "Injekcija dogodka tipa odmor kabla",
        "sim.quick.add_suspicious": "Dodaj sumljive ladje zdaj",
        "sim.quick.add_suspicious.desc": "Takojšen nevarnostni morski kontakt v središču mape",
        "sim.quick.add_uav": "Dodaj nevarnostni UAV zdaj",
        "sim.quick.add_uav.desc": "Takojšen zračni kontakt blizu trenutnega območja",
        "sim.quick.trigger_jamming": "Aktiviraj interferenco zdaj",
        "sim.quick.trigger_jamming.desc": "Takojšnja EW anomalija v trenutnem območju",
        "sim.quick.trigger_cable": "Aktiviraj kabelski alarm zdaj",
        "sim.quick.trigger_cable.desc": "Takojšen dogodek z infrastrukturo blizu sredine mape",
        "sim.show_advanced": "Prikaži napredno postavitev",
        "sim.form.name": "Ime",
        "sim.form.type": "Tip",
        "sim.form.allegiance": "Pripadnost",
        "sim.form.speed": "Hitrost (kts)",
        "sim.form.heading": "Smer",
        "sim.form.latitude": "Latituda",
        "sim.form.longitude": "Longituda",
        "sim.form.jamming_radius": "Polredus interferenčnega vpliva (mn)",
        "sim.form.ais_off": "AIS izklopljeno",
        "sim.form.position": "Pozicija",
        "sim.form.add_unit": "Dodaj enoto",
        "sim.form.cancel": "Ankance",
        "sim.option.vessel": "Ladja",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Podvodna ladja",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferenca",
        "sim.option.cable_event": "Kabelski dogodek",
        "sim.option.hostile": "Nevarnostna",
        "sim.option.friendly": "Zgonska",
        "sim.option.neutral": "Nevtralna"
    },
    "et": {
        "header.badge.disconnected": "Katkeldatud eemaldatud",
        "header.threat": "Uhing",
        "scenario.baltic": "Baltiuba",
        "scenario.arctic": "Arktika",
        "scenario.mediterranean": "Mediterrane",
        "btn.start": "Alusta",
        "btn.stop": "Pidi",
        "subheader.what": "Mis see on:",
        "subheader.what.text": "reael-aegne otsustusjõu toetuse keskkond, mis võtab vastu sinteti∣sed kontaktiid, uuendab uhingu olekut, genereerib konsultatiivseid COA-id, simuleerib tulemusi ja soovitab paketti.",
        "guide.step1": "1. Valige stsenaarium",
        "guide.step2": "2. Vajuta Alusta",
        "guide.step3": "3. Vaadake, kuidas kontaktiid ja uhing muutuvad",
        "guide.step4": "4. Kontrollige COA-id / paketti",
        "guide.step5": "5. Kasutage Simulaatori ühikute süurtmiseks või redigeerimiseks",
        "guide.step6": "6. Genereerige briefing",
        "why.changed": "Mis muutus",
        "map.style": "Kaardi stiil",
        "map.style.osm_standard": "Standardne OpenStreetMap",
        "map.style.osm_humanitarian": "OSM humanitaarne",
        "map.style.carto_light": "Carto kerge",
        "map.style.carto_dark": "Carto tumed",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtreeri ühikud",
        "map.filter.friendly": "Liitlikud",
        "map.filter.hostile": "Võruses",
        "map.filter.neutral": "Neutraalsed",
        "map.filter.air": "Ilma",
        "map.filter.naval": "Mere",
        "map.filter.land": "Maal",
        "map.filter.infra": "Infrastruktuur",
        "map.filter.cable_routes": "Näita kaabelteed",
        "map.filter.noaa_traffic": "Näita NOAA liiklus replay",
        "tab.guide": "Juhend",
        "tab.contacts": "Kontaktiid",
        "tab.coas": "COA-d",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulaator",
        "tab.log": "Log",
        "guide.how_title": "Kuidas süsteem töötab",
        "guide.how.1": "Mootor väljastab või vastab kontaktiidena nagu laevad, UAV-d, interferentsiautomaatide ja kaabeli sündmused.",
        "guide.how.2": "Iga uus kontakt uuendab reaal-aegset olekut ja kontaktiide ajalugu.",
        "guide.how.3": "Analüüsring laskeb uuesti anomaliaindikaatorid ja uhingu tõenäosus iga üksuse kohta.",
        "guide.how.4": "COA-mootor genereerib valikuid reeglite põhjal. See ei luba LLM-le tegevusi valehtada.",
        "guide.how.5": "Iga COA simuleeritakse ja hindatakse. Seejärel kontrollib allokator, kas koordineeritud pakett mitu COA-dest on tõeliselt võimalik olemasolevate vahenditega.",
        "guide.how.6": "Süsteem esile tõstab parima soovituse ja võib nõudluse korral genereerida käskaja-stiilisega briefingi.",
        "guide.control_title": "Mida sa kontrollid",
        "guide.control.1": "<b>Stsenaarium:</b> valige sinteti∣ne operatiivne ala ja uhingu stsenaariumise evolutsioon.",
        "guide.control.2": "<b>Alusta / Pidi:</b> alustab või peatab reaal-aegse tikide ringi.",
        "guide.control.3": "<b>Kaart:</b> vasak pool näitab alati kontaktiide ajakorda pilti.",
        "guide.control.4": "<b>NOAA Liiklus Replay:</b> valikuline NOAA AIS ajalooliste jäljede kiht, mis on paigutatud stsenaariumisse demo käitumise jaoks.",
        "guide.control.5": "<b>Simulaator:</b> süurtab, redigeerib, kustutab või stsenaariumise ühikute käitumist.",
        "guide.control.6": "<b>Briefing:</b> genereerib selge kirjelduse ajakorda soovitust. ",
        "guide.steps_title": "Samm samm",
        "guide.steps.1": "Ava see dashboard ja valige üla balkis stsenaarium.",
        "guide.steps.2": "Vajuta <b>Alusta</b>. Mootor hakkab edema liikumist ja olukord areneb.",
        "guide.steps.3": "Vaadake vasakul kaardi ja pealkirjas <b>Uhing</b> indikaatorit. Kui see hüppab KÕRGE või KRITIILSEks, on analüüs tuvastanud olulise muutuse.",
        "guide.steps.4": "Ava <b>Kontaktiid</b> vaataks teil aktiivseid ühikuid ja hoiatusmärke.",
        "guide.steps.5": "Ava <b>COA-d</b> vaataks teil klassifitseeritud valikuid. Kui on koordineeritud pakett, ilmub see üksikute COA-de päriba.",
        "guide.steps.6": "Ava <b>Simulaator</b>, kui soovite kaardile uue ühiku paigutada või manööri, interferentsi või lähenemist sunnastada.",
        "guide.steps.7": "Vajuta <b>Genereerige briefing</b>, kui soovite lühikese operatiivse kokkuvõte.",
        "guide.callout.major_change": "Mis arvatakse oluliseks muutuseks?",
        "guide.callout.major_change.text": "Näiteks: laev pöördub infrastruktuuri poole, kiirustab kaabeli läheduses, ilmub UAV aeropordi läheduses, väljastatakse interferents või muutub soovitatud COA.",
        "guide.callout.bundle_q": "Mis on pakett?",
        "guide.callout.bundle_a": "Pakett on lihtsalt mitu konsultatiivseid COA-d, mis on ühesolgis, näiteks varj – ISR – kaabeli kaitse. See ei ole eraldi või salane režiim.",
        "guide.callout.not_doing": "Mida süsteem ei tee:",
        "guide.callout.not_doing.text": "see ei täita käskeid, ei allokeeri relvaid ega autoriseeri konfliktide autonoomselt.",
        "contacts.stat.contacts": "Kontaktiidud",
        "contacts.stat.tracks": "Jäljed",
        "contacts.stat.coas": "COA-d",
        "contacts.stat.processed": "Kõrgitatud",
        "briefing.generate": "Genereerige briefing",
        "briefing.download_pdf": "Laadi alla PDF",
        "briefing.download_pdf_en": "Laadi alla PDF (EN)",
        "sim.quick_scenarios": "Kiired stsenaariumid",
        "sim.quick_desc": "Kasuta neid eelneavalikuid, kui soovite, et mootor nähtavalt reageeriks. Võruses ja tuntud välist kontaktiid kohendavad rõhku. Liitlike patrolli ja ISR parandavad saadaval toetust ja võivad avada tugevamaid koordineeritud pakette.",
        "sim.play.maritime_threat": "Mereuhing kaabeli lähedal",
        "sim.play.maritime_threat.desc": "Süurtab võruse laeva infrastruktuuri lähedal AIS välja lülitatud ja kahtlase käitumisega madalal kiiruses",
        "sim.play.uav_airport": "UAV aeropordi lähedal",
        "sim.play.uav_airport.desc": "Süurtab võruse UAV-d ilma õhuruumi ohtlikuse signatuuriga",
        "sim.play.ew_escalation": "EW eskalatsioon",
        "sim.play.ew_escalation.desc": "Süurtab interferentsia allika ajakorda operatiivses ala.",
        "sim.play.allied_isr": "Lisa liitlik ISR toetus",
        "sim.play.allied_isr.desc": "Süurtab liitlik UAV/toetuse aktiiv, et testida asendimuutusi",
        "sim.play.allied_patrol": "Lisa liitlik patroll",
        "sim.play.allied_patrol.desc": "Süurtab liitlik patrolllaeva alale.",
        "sim.play.cable_alert": "Infrastruktuuri juhtum",
        "sim.play.cable_alert.desc": "Süurtab kaabeli sündmuse tüüpi hoiatus kaardi keskas.",
        "sim.undo_last": "Tühista viimane süurtmine",
        "sim.reset_scenario": "Taaskehenda stsenaarium",
        "sim.preset.suspicious_vessel": "Kahtlase laev",
        "sim.preset.suspicious_vessel.desc": "Võruse laev kaardi ajakorda keskas",
        "sim.preset.hostile_uav": "Võruse UAV",
        "sim.preset.hostile_uav.desc": "UAV kõrge ohtlikuse signatuuriga",
        "sim.preset.jamming_event": "Interferentsia sündmus",
        "sim.preset.jamming_event.desc": "Süurtab interferentsia kontaktiidi, mis mõjutab anomaaliaid",
        "sim.preset.cable_event": "Kaabeli sündmus",
        "sim.preset.cable_event.desc": "Süurtab kaabeli katkemise tüüpi sündmuse",
        "sim.quick.add_suspicious": "Lisa kohe kahtlas laev",
        "sim.quick.add_suspicious.desc": "Kohe võruse merekontakt kaardi keskas",
        "sim.quick.add_uav": "Lisa kohe võruse UAV",
        "sim.quick.add_uav.desc": "Kohe ilmakontakt ajakorda lähedal",
        "sim.quick.trigger_jamming": "Aktiveeri kohe interferentsia",
        "sim.quick.trigger_jamming.desc": "Kohe EW tüüpi anomaalia ajakorda lähedal",
        "sim.quick.trigger_cable": "Aktiveeri kohe kaabeli hoiatus",
        "sim.quick.trigger_cable.desc": "Kohe infrastruktuuri juhtum kaardi keskas",
        "sim.show_advanced": "Näita edasine paigutus",
        "sim.form.name": "Nimi",
        "sim.form.type": "Tüüp",
        "sim.form.allegiance": "Liitlikkus",
        "sim.form.speed": "Kiirus (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Latitiud",
        "sim.form.longitude": "Longitiud",
        "sim.form.jamming_radius": "Interferentsia raio (mn)",
        "sim.form.ais_off": "AIS välja lülitatud",
        "sim.form.position": "Asukoht",
        "sim.form.add_unit": "Lisa ühik",
        "sim.form.cancel": "Tühista",
        "sim.option.vessel": "Laev",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarine",
        "sim.option.convoy": "Konvooi",
        "sim.option.jamming": "Interferents",
        "sim.option.cable_event": "Kaabeli sündmus",
        "sim.option.hostile": "Võruses",
        "sim.option.friendly": "Liitlik",
        "sim.option.neutral": "Neutraal"
    },
    "lv": {
        "header.badge.disconnected": "Atvienots",
        "header.threat": "Apar skaļa",
        "scenario.baltic": "Baltijas jūras",
        "scenario.arctic": "Arktika",
        "scenario.mediterranean": "Vidzemres",
        "btn.start": "Sākt",
        "btn.stop": "Pārtraukt",
        "subheader.what": "Kas tas ir:",
        "subheader.what.text": "tiesa laika izgriezeniskās atbalsta vidi, kas ņem sintētiskus kontaktus, atjaunina apdraudējuma stāvokli, ģenerē konsultatīvas COA, simuliē rezultātus un iesaka paketi.",
        "guide.step1": "1. Izvēlēties scenāriju",
        "guide.step2": "2. Noklikšķināt uz Sākt",
        "guide.step3": "3. Pamanīt, kā mainās kontakti un apdraudējums",
        "guide.step4": "4. Pārskatīt COA / paketi",
        "guide.step5": "5. Izmantot Simulators, lai injektētu vai rediētu vienības",
        "guide.step6": "6. Ģenerēt briefingu",
        "why.changed": "Kas mainījās",
        "map.style": "Kartas stils",
        "map.style.osm_standard": "OpenStreetMap standarta",
        "map.style.osm_humanitarian": "OSM humanitārs",
        "map.style.carto_light": "Carto viegls",
        "map.style.carto_dark": "Carto tumšs",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrai vienības",
        "map.filter.friendly": "Aliētie",
        "map.filter.hostile": "Hostili",
        "map.filter.neutral": "Neitrali",
        "map.filter.air": "Gaisa",
        "map.filter.naval": "Jūras",
        "map.filter.land": "Savestras",
        "map.filter.infra": "Infrastruktūra",
        "map.filter.cable_routes": "Rādīt kabelu maršrutus",
        "map.filter.noaa_traffic": "Rādīt NOAA trafika atspoguļojumu",
        "tab.guide": "Vads",
        "tab.contacts": "Kontakti",
        "tab.coas": "COA",
        "tab.briefing": "Briefings",
        "tab.simulator": "Simulators",
        "tab.log": "Žurnāls",
        "guide.how_title": "Kā darbojas sistēma",
        "guide.how.1": "Dzinis sūta vai saņem kontaktus kā kuģus, UAV, interferenču ziņojumus un kabelu notikumu.",
        "guide.how.2": "Katrs jauns kontakts atjaunina tiesa laika stāvokli un kontaktu vēsturi.",
        "guide.how.3": "Analīzes cikls atkalkulē anomāliju indikatorus un apdraudējuma iespējamību pa entitāti.",
        "guide.how.4": "COA dzinis ģenerē iespējas, balstoties uz noteikumiem. Tas neļauj LLM izgaldot darbības.",
        "guide.how.5": "Katru COA simuliē un vērtē. Pēc tam aprakstītājs pārbauda, vai koordinēts pakets vairāku COA ir patiešām iespējams ar pašreizējām līdzekļiem.",
        "guide.how.6": "Sistēma uzsver labāko rekomendāciju un var ģenerēt komandiera stila briefingu pēc pieprasījuma.",
        "guide.control_title": "Ko jūs kontrolējat",
        "guide.control.1": "<b>Scenārijs:</b> izvēli sintētiskā operacionālajā zonā un scenārijiskajā apdraudējuma evolūcijā.",
        "guide.control.2": "<b>Sākt / Pārtraukt:</b> sāka vai pārtrauc tiesa laika tiks ciklu.",
        "guide.control.3": "<b>Karte:</b> kreisā pusē vienmēr parādās kontaktu pašreizējais attēls.",
        "guide.control.4": "<b>NOAA Trafika Atspoguļojums:</b> papildu slānis ar NOAA vēsturiskajām AIS izkārtojumiem scenārijā demo uzvedības veikšanai.",
        "guide.control.5": "<b>Simulators:</b> injekta, rediē, dzēš vai scenārijizē vienību uzvedību.",
        "guide.control.6": "<b>Briefings:</b> ģenerē lasīgu aprakstu par pašreizējo rekomendāciju.",
        "guide.steps_title": "Pasākumi",
        "guide.steps.1": "Atveriet šo paneli un izvēlieties scenāriju augšējā joslā.",
        "guide.steps.2": "Noklikšķiniet uz <b>Sākt</b>. Dzinis sāka progresēt un situācija evoluēj. ",
        "guide.steps.3": "Pamaniet karti kreisajā pusē un <b>Apar skaļa</b> indikatoru virsrakstā. Ja tas pāriet uz AUGSTU vai KRĪTISKO, analīze ir pamanīja saistīgu izmaiņu.",
        "guide.steps.4": "Atveriet <b>Kontakti</b>, lai redzētu aktīvās vienības un brīdinājumu zīmeces.",
        "guide.steps.5": "Atveriet <b>COA</b>, lai pārskatītu klasificētās iespējas. Ja ir koordinēts pakets, tas parādās virs atsevišķām COA.",
        "guide.steps.6": "Atveriet <b>Simulators</b>, ja vēlaties ievietot jaunu vienību kartā vai spēlot maniobru, interferenci vai piegārdīgu.",
        "guide.steps.7": "Noklikšķiniet uz <b>Ģenerēt briefingu</b>, kad vēlaties koncīzu operacionālo kopsavilkumu.",
        "guide.callout.major_change": "Kas skaita parzīmīgu izmaiņu?",
        "guide.callout.major_change.text": "Piemēri: kuģis kreisās uz infrastruktūru, pēkšņi pie kable, parādās UAV pie aerodroma, tiek sūtīta interferencija vai mainās ieteiktais COA.",
        "guide.callout.bundle_q": "Kas ir pakets?",
        "guide.callout.bundle_a": "Pakets ir vienkārši vairāki konsultatīvi COA, kas nozīmē kopā, piemēram, ēna + ISR + kabela aizsardzība. Tas nav atsevišķs vai misteriēts režīms.",
        "guide.callout.not_doing": "Kas sistēma *ne* dara:",
        "guide.callout.not_doing.text": "tas neizpilda rīkojumus, neapgādā ieroču un neautorizē šaušanas autonomi.",
        "contacts.stat.contacts": "Kontakti",
        "contacts.stat.tracks": "Izsekošanas maršruti",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Apstrādāti",
        "briefing.generate": "Ģenerēt briefingu",
        "briefing.download_pdf": "Lejupielādēt PDF",
        "briefing.download_pdf_en": "Lejupielādēt PDF (EN)",
        "sim.quick_scenarios": "Ātri scenāriji",
        "sim.quick_desc": "Izmantojiet šos iestatījumus, ja vēlaties, lai dzinis reaģētu redzami. Hostili un zināmi kontakti palielina spiedienu. Aliēto patrulju un ISR uzlabo pieejamo atbalstu un var atbloķēt spēcīgākus koordinētos paketus.",
        "sim.play.maritime_threat": "Jūras apdraudējums pie kable",
        "sim.play.maritime_threat.desc": "Injektē hostilu kuģi pie infrastruktūras ar izslēgto AIS un aizdomīgu zemā ātruma uzvedību",
        "sim.play.uav_airport": "UAV pie aerodroma",
        "sim.play.uav_airport.desc": "Injektē hostilu UAV ar gaisa telpas riska zīmējumu",
        "sim.play.ew_escalation": "EW eskalācija",
        "sim.play.ew_escalation.desc": "Injektē interferenču avotu pašreizējā operacionālajā zonā",
        "sim.play.allied_isr": "Pievienot aliēto ISR atbalstu",
        "sim.play.allied_isr.desc": "Injektē draudzīgu UAV/atbalsta aktīvu, lai testētu pozīcijas izmaiņas",
        "sim.play.allied_patrol": "Pievienot aliēto patrulju",
        "sim.play.allied_patrol.desc": "Injektē aliēto patrulju kuģi zonā",
        "sim.play.cable_alert": "Infrastruktūras incidents",
        "sim.play.cable_alert.desc": "Injektē kabela notikumu tipa brīdinājumu kartes vidus",
        "sim.undo_last": "Atgriezties iepriekšējā injekcija",
        "sim.reset_scenario": "Atjaunot scenāriju",
        "sim.preset.suspicious_vessel": "Aizdomīgs kuģis",
        "sim.preset.suspicious_vessel.desc": "Hostilus kuģis pie pašreizējās kartes vidus",
        "sim.preset.hostile_uav": "Hostilus UAV",
        "sim.preset.hostile_uav.desc": "UAV ar paaugstinātu apdraudējuma zīmējumu",
        "sim.preset.jamming_event": "Interferenču notikums",
        "sim.preset.jamming_event.desc": "Injektē interferenču kontaktu, kas ietekmē anomālijas",
        "sim.preset.cable_event": "Kabela notikums",
        "sim.preset.cable_event.desc": "Injektē kabela pārtraukuma notikumu tipu",
        "sim.quick.add_suspicious": "Pievienot aizdomīgu kuģi tagad",
        "sim.quick.add_suspicious.desc": "Tiesais jūras kontakts vidus kartes",
        "sim.quick.add_uav": "Pievienot hostilu UAV tagad",
        "sim.quick.add_uav.desc": "Tiesais gaisa kontakts pašreizējās zonas tuvumā",
        "sim.quick.trigger_jamming": "Aktīvēt interferenci tagad",
        "sim.quick.trigger_jamming.desc": "Tiesais EW anomālijs pašreizējā zonā",
        "sim.quick.trigger_cable": "Aktīvēt kabela brīdinājumu tagad",
        "sim.quick.trigger_cable.desc": "Tiesais infrastruktūras incidents kartes vidus",
        "sim.show_advanced": "Rādīt papildu izvietojumu",
        "sim.form.name": "Vārds",
        "sim.form.type": "Tips",
        "sim.form.allegiance": "Piemērošana",
        "sim.form.speed": "Ātrums (kts)",
        "sim.form.heading": "Kursas",
        "sim.form.latitude": "Latitūda",
        "sim.form.longitude": "Longitūda",
        "sim.form.jamming_radius": "Interferenču rādiuss (mn)",
        "sim.form.ais_off": "AIS izslēgts",
        "sim.form.position": "Pozīcija",
        "sim.form.add_unit": "Pievienot vienību",
        "sim.form.cancel": "Atcelter",
        "sim.option.vessel": "Kuģis",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarin",
        "sim.option.convoy": "Konvojs",
        "sim.option.jamming": "Interferencija",
        "sim.option.cable_event": "Kabela notikums",
        "sim.option.hostile": "Hostilus",
        "sim.option.friendly": "Aliēts",
        "sim.option.neutral": "Neitrals"
    },
    "lt": {
        "header.badge.disconnected": "Atsitintas",
        "header.threat": "Įvertinimas",
        "scenario.baltic": "Baltijos jūra",
        "scenario.arctic": "Arktika",
        "scenario.mediterranean": "Viduržemio jūra",
        "btn.start": "Pradėti",
        "btn.stop": "Stop",
        "subheader.what": "Kas tai yra:",
        "subheader.what.text": "gyvų sprendimų palaikymo aplinka, kuri įsijungia sintetiniais kontaktais, atnaujina grėsmės būklę, generuoja konsultatyvius COA, simuliuoja rezultatus ir rekomenduojama paketą.",
        "guide.step1": "1. Pasirinkti scenarijų",
        "guide.step2": "2. Spustelėti Pradėti",
        "guide.step3": "3. Pastebėti, kaip keičiasi kontaktai ir grėsmė",
        "guide.step4": "4. Peržiūrėti COA / paketą",
        "guide.step5": "5. Naudoti Simuliatorius, kad įsijungtumėte arba redaguotumėte vienetų",
        "guide.step6": "6. Generuoti brifingą",
        "why.changed": "Kas keitėsi",
        "map.style": "Kartos stilius",
        "map.style.osm_standard": "Standartinis OpenStreetMap",
        "map.style.osm_humanitarian": "OSM humanitarinis",
        "map.style.carto_light": "Carto šviesus",
        "map.style.carto_dark": "Carto tamsus",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtruoti vienetes",
        "map.filter.friendly": "Aliija",
        "map.filter.hostile": "Įsileigę",
        "map.filter.neutral": "Neutralūs",
        "map.filter.air": "Gaisrinės",
        "map.filter.naval": "Jūrinės",
        "map.filter.land": "Žemės",
        "map.filter.infra": "Infrastruktūra",
        "map.filter.cable_routes": "Rodyti kabelių maršrutus",
        "map.filter.noaa_traffic": "Rodyti NOAA tinklo peržiūrą",
        "tab.guide": "Gidas",
        "tab.contacts": "Kontaktai",
        "tab.coas": "COA",
        "tab.briefing": "Brifingas",
        "tab.simulator": "Simuliatorius",
        "tab.log": "Žurnalas",
        "guide.how_title": "Kaip veikia sistema",
        "guide.how.1": "Variklis išsiunčia arba gauna kontaktus kaip laivus, UAV, interferencijos pranešimus ir kabelių įvykius.",
        "guide.how.2": "Kiekvienas naujas kontaktas atnaujina gyvą būklę ir kontaktų istoriją.",
        "guide.how.3": "Analizės ciklas perenkalkuliuoja anomalių rodiklius ir grėsmės tikimybę pagal entitetą.",
        "guide.how.4": "COA variklis generuoja variantus pagal taisykles. Jis neleidžia LLM išgalvoti veiksmų.",
        "guide.how.5": "Kiekvienas COA simuliuojamas ir įvertinamas. Po to paskirstytojas patikrina, ar koordinuotas COA paketas iš tikrųjų yra įgyvendinamas su dabartiniais vidutais.",
        "guide.how.6": "Sistema išskiria geriausią rekomendaciją ir gali generuoti komandanso stiliaus brifingą pagal pageidavimą.",
        "guide.control_title": "Kas kontroliuojate",
        "guide.control.1": "<b>Scenarijus:</b> pasirinkite sintetinę operacinę teritoriją ir grėsmės scenarijų evoliuciją.",
        "guide.control.2": "<b>Pradėti / Stop:</b> pradeda arba sustabdo gyvų tiksų ciklą.",
        "guide.control.3": "<b>Kartos:</b> kairėje pusėje visada rodoma kontakto dabartinė matninė.",
        "guide.control.4": "<b>NOAA Tinklo Peržiūra:</b> papildoma sluoksnis NOAA istorinių AIS trajektorijų, išdėstytų scenarijuje demo elgesio užtikrinimui.",
        "guide.control.5": "<b>Simuliatorius:</b> įsijungia, redaguoja, pašalina arba scenarijuje vienetų elgesį.",
        "guide.control.6": "<b>Brifingas:</b> generuoja lengvai skaitomą aprašymą apie dabartinę rekomendaciją.",
        "guide.steps_title": "Žingsnis po žingsnio",
        "guide.steps.1": "Atidarykite šį kontrolpanelį ir pasirinkite scenarijų viršuje.",
        "guide.steps.2": "Spustelėkite <b>Pradėti</b>. Variklis pradeda judėti, o situacija evoliuoti.",
        "guide.steps.3": "Pastebėkite kartą kairėje ir <b>Grėsmės</b> rodiklį viršuje. Jei jis šoktelės į VYSIENĄ ar KRITIŠIĄ, analizė aptiko reikšmingą pokytį.",
        "guide.steps.4": "Atidarykite <b>Kontaktai</b>, kad pamatytumėte aktyvias vienetes ir įspėjimo ženklistus.",
        "guide.steps.5": "Atidarykite <b>COA</b>, kad peržiūrėtumėte klasifikuotas variantus. Jei egzistuoja koordinuotas paketas, jis pasirodys virš individualių COA.",
        "guide.steps.6": "Atidarykite <b>Simuliatorius</b>, jei norite įdėti naują vienetą į kartą arba įmusinti manevrą, interferenciją ar pabrėžimą.",
        "guide.steps.7": "Spustelėkite <b>Generuoti brifingą</b>, kai norite koncizuotą operacinį santrauką.",
        "guide.callout.major_change": "Kas laikoma dideliu pokyčiu?",
        "guide.callout.major_change.text": "Pavyzdžiai: laivas sukasi į infrastruktūrą, apvaizduoja prie kabelio, pasirodo UAV prie oro uostos, išsiunčiamas interferencijos ar keičiama rekomenduojama COA.",
        "guide.callout.bundle_q": "Kas yra paketas?",
        "guide.callout.bundle_a": "Paketas yra tiesiog kelis konsultatyvūs COA, kurie turi smulkiai reikšti kartu, pvz., šešėlis + ISR + kabelio apsauga. Tai nėra atskiras ar mistinis režimas.",
        "guide.callout.not_doing": "Kas sistema NEpadaro:",
        "guide.callout.not_doing.text": "neįvydo įsakymų, neišskiria gūnų ir neautorizuoja konfrontacijų autonomiškai.",
        "contacts.stat.contacts": "Kontaktai",
        "contacts.stat.tracks": "Trajektorijos",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Apdoroti",
        "briefing.generate": "Generuoti brifingą",
        "briefing.download_pdf": "Atsisiųsti PDF",
        "briefing.download_pdf_en": "Atsisiųsti PDF (EN)",
        "sim.quick_scenarios": "Greitos scenarijai",
        "sim.quick_desc": "Naudokite šiuos išankstinius nustatymus, jei norite, kad variklis reaguotų matoma. Įsileigiantys ir nežinomi kontaktai didina spaudimą. Aliijos patrolybė ir ISR pagerina prieinamą pagalbą ir gali atlaisvinti stipresnius koordinuotus paketus.",
        "sim.play.maritime_threat": "Jūrinė grėsmė prie kabelio",
        "sim.play.maritime_threat.desc": "Įsijungia įsileigiantis laivas prie infrastruktūros su išjungtu AIS ir įtarudžiu elgesiu žemoje greičiu",
        "sim.play.uav_airport": "UAV prie oro uostos",
        "sim.play.uav_airport.desc": "Įsijungia įsileigiantis UAV su oro erdvės rizikos ženklu",
        "sim.play.ew_escalation": "EW eskalavimas",
        "sim.play.ew_escalation.desc": "Įsijungia interferencijos šaltinis dabartinėje operacijoje",
        "sim.play.allied_isr": "Pridėti aliijos ISR pagalbą",
        "sim.play.allied_isr.desc": "Įsijungia draugiškas UAV/ISR pagalbos vienetas, kad išbandytų pozicijos pokyčius",
        "sim.play.allied_patrol": "Pridėti aliijos patrolį",
        "sim.play.allied_patrol.desc": "Įsijungia draugiškas patrolio laivas zonoje",
        "sim.play.cable_alert": "Infrastruktūros įvykis",
        "sim.play.cable_alert.desc": "Įsijungia kabelio įvykio įspėjimas prie kartos centro",
        "sim.undo_last": "Atšaukti paskutinį įsijungimą",
        "sim.reset_scenario": "Atkurti scenarijų",
        "sim.preset.suspicious_vessel": "Įtarudžius laivas",
        "sim.preset.suspicious_vessel.desc": "Įsileigiantis laivas prie kartos dabartinio centro",
        "sim.preset.hostile_uav": "Įsileigiantis UAV",
        "sim.preset.hostile_uav.desc": "UAV su didelės grėsmės ženklu",
        "sim.preset.jamming_event": "Interferencijos įvykis",
        "sim.preset.jamming_event.desc": "Įsijungia interferencijos kontaktas, kuris veikia anomalioms",
        "sim.preset.cable_event": "Kabelio įvykis",
        "sim.preset.cable_event.desc": "Įsijungia kabelio pažeidimo tipo įvykis",
        "sim.quick.add_suspicious": "Dabar pridėti įtarudžius laivą",
        "sim.quick.add_suspicious.desc": "Immediatas įsileigiantis jūrinis kontaktas kartos centre",
        "sim.quick.add_uav": "Dabar pridėti įsileigiantį UAV",
        "sim.quick.add_uav.desc": "Immediatas gaisrinės kontaktas prie dabartinės zonos",
        "sim.quick.trigger_jamming": "Dabar įjungti interferenciją",
        "sim.quick.trigger_jamming.desc": "Immediatas EW anomalia dabartinėje zonoje",
        "sim.quick.trigger_cable": "Dabar įjungti kabelio įspėjimą",
        "sim.quick.trigger_cable.desc": "Immediatas infrastruktūros įvykis prie kartos centro",
        "sim.show_advanced": "Rodyti išsamią išdėstymą",
        "sim.form.name": "Pavadinimas",
        "sim.form.type": "Tipas",
        "sim.form.allegiance": "Pilmystė",
        "sim.form.speed": "Greičis (kts)",
        "sim.form.heading": "Kurvis",
        "sim.form.latitude": "Latitudas",
        "sim.form.longitude": "Longitudas",
        "sim.form.jamming_radius": "Interferencijos radias (mn)",
        "sim.form.ais_off": "AIS išjungtas",
        "sim.form.position": "Pozicija",
        "sim.form.add_unit": "Pridėti vienetą",
        "sim.form.cancel": "Atšaukti",
        "sim.option.vessel": "Laivas",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarinė",
        "sim.option.convoy": "Konvojus",
        "sim.option.jamming": "Interferencija",
        "sim.option.cable_event": "Kabelio įvykis",
        "sim.option.hostile": "Įsileigiantis",
        "sim.option.friendly": "Aliija",
        "sim.option.neutral": "Neutralus"
    },
    "da": {
        "header.badge.disconnected": "Afkoblet",
        "header.threat": "Trussel",
        "scenario.baltic": "Østersøen",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Middelhavet",
        "btn.start": "Start",
        "btn.stop": "Stop",
        "subheader.what": "Hvad er dette:",
        "subheader.what.text": "et live beslutningsstøtte miljø, der indtager syntetiske kontakter, opdaterer trusselsstatus, genererer konsultative COA'er, simulerer resultater og anbefaler en pakke.",
        "guide.step1": "1. Vælg scenarie",
        "guide.step2": "2. Tryk Start",
        "guide.step3": "3. Observer ændringer i kontakter og trussel",
        "guide.step4": "4. Gennemgå COA'er / pakke",
        "guide.step5": "5. Brug Simulatoren til at injicere eller redigere enheder",
        "guide.step6": "6. Generer briefing",
        "why.changed": "Hvad ændrede sig",
        "map.style": "Kortstil",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM humanitær",
        "map.style.carto_light": "Carto lys",
        "map.style.carto_dark": "Carto mørk",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrer enheder",
        "map.filter.friendly": "Venlige",
        "map.filter.hostile": "Fiendtlige",
        "map.filter.neutral": "Neutrale",
        "map.filter.air": "Luftfartøjer",
        "map.filter.naval": "Søfartøjer",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastruktur",
        "map.filter.cable_routes": "Vis kableruter",
        "map.filter.noaa_traffic": "Vis NOAA replay trafik",
        "tab.guide": "Guide",
        "tab.contacts": "Kontakter",
        "tab.coas": "COA'er",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Log",
        "guide.how_title": "Hvordan systemet fungerer",
        "guide.how.1": "Motoren udsender eller modtager kontakter som skibe, UAV'er, interferensrapporter og kabelhændelser.",
        "guide.how.2": "Hver ny kontakt opdaterer live status og kontakthistorik.",
        "guide.how.3": "Analysecyklussen genberegner anomaliindikatorer og trussels sandsynligheder pr. enhed.",
        "guide.how.4": "COA-motoren genererer valg baseret på regler. Den tillader ikke LLM at opfinde handlinger.",
        "guide.how.5": "Hver COA simuleres og scores. Derefter kontrollerer tildeleren, om en koordineret pakke af flere COA'er er virkelig gennemførlig med de nuværende midler.",
        "guide.how.6": "Systemet fremhæver den bedste anbefaling og kan generere en kommandør-stil briefing efter behov.",
        "guide.control_title": "Hvad du kontrollerer",
        "guide.control.1": "<b>Scenarie:</b> vælg det syntetiske operationsområde og den manuskriptbaserede trusseludvikling.",
        "guide.control.2": "<b>Start / Stop:</b> starter eller stopper live tick-cyklussen.",
        "guide.control.3": "<b>Kort:</b> venstre side viser altid den aktuelle kontaktbillede.",
        "guide.control.4": "<b>NOAA Trafik Replay:</b> valgfri lag af historiske AIS-spor fra NOAA genplaceret i scenariet for demoadfærd.",
        "guide.control.5": "<b>Simulator:</b> injicerer, redigerer, sletter eller manuskripter enhedsadfærd.",
        "guide.control.6": "<b>Briefing:</b> genererer en læsbar forklaring af den aktuelle anbefaling.",
        "guide.steps_title": "Trin for trin",
        "guide.steps.1": "Åbn dette dashboard og vælg et scenarie i topbjælken.",
        "guide.steps.2": "Tryk <b>Start</b>. Motoren begynder at fremskride, og situationen udvikler sig.",
        "guide.steps.3": "Observer kortet til venstre og <b>Trussel</b>-indikatoren i toppen. Hvis den springer til HØJ eller KRITISK, har analysen detekteret en relevant ændring.",
        "guide.steps.4": "Åbn <b>Kontakter</b> for at se aktive enheder og alarmer.",
        "guide.steps.5": "Åbn <b>COA'er</b> for at gennemgå klassificerede muligheder. Hvis der findes en koordineret pakke, vises den over de individuelle COA'er.",
        "guide.steps.6": "Åbn <b>Simulator</b> hvis du vil placere en ny enhed på kortet eller tvinge en manøvre, interferens eller tilnærmelse.",
        "guide.steps.7": "Tryk <b>Generer briefing</b> når du ønsker et kortfattet operationelt resumé.",
        "guide.callout.major_change": "Hvad tæller som en vigtig ændring?",
        "guide.callout.major_change.text": "Eksempler: et skib drejer mod infrastruktur, patruljerer nær en kabel, en UAV dukker op nær lufthavnen, der udsendes interferens eller den anbefalede COA ændres.",
        "guide.callout.bundle_q": "Hvad er en pakke?",
        "guide.callout.bundle_a": "En pakke er blot flere konsultative COA'er, der giver mening sammen, f.eks. skygge + ISR + kabelbeskyttelse. Det er ikke en separat eller mystisk tilstand.",
        "guide.callout.not_doing": "Hvad systemet IKKE gør:",
        "guide.callout.not_doing.text": "den udfører ikke ordrer, tildeler ikke våben og autoriserer ikke konfrontationer autonomt.",
        "contacts.stat.contacts": "Kontakter",
        "contacts.stat.tracks": "Spor",
        "contacts.stat.coas": "COA'er",
        "contacts.stat.processed": "Behandlede",
        "briefing.generate": "Generer briefing",
        "briefing.download_pdf": "Download PDF",
        "briefing.download_pdf_en": "Download PDF (EN)",
        "sim.quick_scenarios": "Hurtige scenarier",
        "sim.quick_desc": "Brug disse forudindstillinger, hvis du vil have motoren til at reagere synligt. Fiendtlige og ukendte kontakter øger presset. Venlig patrulje og ISR forbedrer den tilgængelige støtte og kan låse op for stærkere koordinerede pakker.",
        "sim.play.maritime_threat": "Maritim trussel nær kabel",
        "sim.play.maritime_threat.desc": "Injektér et fjendtligt skib nær infrastruktur med slukket AIS og mistænkelig lav hastighedsadfærd",
        "sim.play.uav_airport": "UAV nær lufthavn",
        "sim.play.uav_airport.desc": "Injektér en fjendtlig UAV med luftrumsrisikoprofil",
        "sim.play.ew_escalation": "EW eskalering",
        "sim.play.ew_escalation.desc": "Injektér en interferenskilde i det aktuelle operationsområde",
        "sim.play.allied_isr": "Tilføj venlig ISR støtte",
        "sim.play.allied_isr.desc": "Injektér en venlig UAV/støtteaktiv for at teste holdningsændringer",
        "sim.play.allied_patrol": "Tilføj venlig patrulje",
        "sim.play.allied_patrol.desc": "Injektér et venligt patruljeskib i zonen",
        "sim.play.cable_alert": "Infrastrukturhændelse",
        "sim.play.cable_alert.desc": "Injektér en kabelhændelseslignende alarm nær midten af kortet",
        "sim.undo_last": "Angre sidste injektion",
        "sim.reset_scenario": "Nulstil scenarie",
        "sim.preset.suspicious_vessel": "Mistænkeligt fartøj",
        "sim.preset.suspicious_vessel.desc": "Fjendtligt skib nær det aktuelle kortcenter",
        "sim.preset.hostile_uav": "Fjendtlig UAV",
        "sim.preset.hostile_uav.desc": "UAV med forhøjet trusselsaftryk",
        "sim.preset.jamming_event": "Interferenshændelse",
        "sim.preset.jamming_event.desc": "Injektér en interferenskontakt, der påvirker anomalier",
        "sim.preset.cable_event": "Kabelhændelse",
        "sim.preset.cable_event.desc": "Injektér en kabelbrud-lignende hændelse",
        "sim.quick.add_suspicious": "Tilføj mistænkeligt skib nu",
        "sim.quick.add_suspicious.desc": "Øjeblikkelig fjendtlig maritim kontakt i kortmidten",
        "sim.quick.add_uav": "Tilføj fjendtlig UAV nu",
        "sim.quick.add_uav.desc": "Øjeblikkelig luftkontakt nær det aktuelle område",
        "sim.quick.trigger_jamming": "Aktiver interferens nu",
        "sim.quick.trigger_jamming.desc": "Øjeblikkelig EW-anomali i det aktuelle område",
        "sim.quick.trigger_cable": "Aktiver kabelalarm nu",
        "sim.quick.trigger_cable.desc": "Øjeblikkelig infrastrukturhændelse nær kortmidten",
        "sim.show_advanced": "Vis avanceret placering",
        "sim.form.name": "Navn",
        "sim.form.type": "Type",
        "sim.form.allegiance": "Tilhørsforhold",
        "sim.form.speed": "Hastighed (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Breddegrad",
        "sim.form.longitude": "Længdegrad",
        "sim.form.jamming_radius": "Interferensradius (mn)",
        "sim.form.ais_off": "AIS slukket",
        "sim.form.position": "Position",
        "sim.form.add_unit": "Tilføj enhed",
        "sim.form.cancel": "Annuller",
        "sim.option.vessel": "Skib",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "U-båd",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferens",
        "sim.option.cable_event": "Kabelhændelse",
        "sim.option.hostile": "Fiendtlig",
        "sim.option.friendly": "Venlig",
        "sim.option.neutral": "Neutral"
    },
    "no": {
        "header.badge.disconnected": "Fra koblet fra",
        "header.threat": "Trussel",
        "scenario.baltic": "Østersjøen",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Middelhavet",
        "btn.start": "Start",
        "btn.stop": "Stopp",
        "subheader.what": "Hva er dette:",
        "subheader.what.text": "et sanntids beslutningsstøtte miljø som tar inn syntetiske kontakter, oppdaterer trusselstatus, genererer rådgivende COAer, simulerer resultater og anbefaler en pakke.",
        "guide.step1": "1. Velg scenario",
        "guide.step2": "2. Trykk Start",
        "guide.step3": "3. Observer hvordan kontakter og trussel endres",
        "guide.step4": "4. Gå gjennom COAer / pakke",
        "guide.step5": "5. Bruk Simulatoren til å injisere eller redigere enheter",
        "guide.step6": "6. Generer briefing",
        "why.changed": "Hva endret seg",
        "map.style": "Kartstil",
        "map.style.osm_standard": "Standard OpenStreetMap",
        "map.style.osm_humanitarian": "Humanitær OSM",
        "map.style.carto_light": "Carto Lys",
        "map.style.carto_dark": "Carto Mørk",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrer enheter",
        "map.filter.friendly": "Allierte",
        "map.filter.hostile": "Fiender",
        "map.filter.neutral": "Nøytrale",
        "map.filter.air": "Luft",
        "map.filter.naval": "Sjø",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastruktur",
        "map.filter.cable_routes": "Vis kableruter",
        "map.filter.noaa_traffic": "Vis NOAA trafikk replay",
        "tab.guide": "Veiledning",
        "tab.contacts": "Kontakter",
        "tab.coas": "COAer",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Logg",
        "guide.how_title": "Hvordan systemet fungerer",
        "guide.how.1": "Motoren sender eller mottar kontakter som skip, UAV, interferensrapporter og kabelhendelser.",
        "guide.how.2": "Hver ny kontakt oppdaterer sanntilstanden og kontakthistorikken.",
        "guide.how.3": "Analyse-loopen regner ut anomalindikatorer og trussel-sannsynligheter per enhet.",
        "guide.how.4": "COA-motoren genererer alternativer basert på regler. Den lar ikke LLM diktere handlinger.",
        "guide.how.5": "Hver COA simuleres og scores. Deretter sjekker tildeleren om en koordinert pakke av flere COAer er virkelig gjennomførbar med de nåværende midlene.",
        "guide.how.6": "Systemet fremhever den beste anbefalingen og kan generere en kommandør-stil briefing på forespørsel.",
        "guide.control_title": "Hva du kontrollerer",
        "guide.control.1": "<b>Scenario:</b> velger det syntetiske operasjonsområdet og den manusstyrte trusselutviklingen.",
        "guide.control.2": "<b>Start / Stopp:</b> starter eller stopper sanntids tick-loopen.",
        "guide.control.3": "<b>Kart:</b> venstre side viser alltid den nåværende kontaktbildet.",
        "guide.control.4": "<b>NOAA Trafikk Replay:</b> valgfri lag av historiske AIS-spor fra NOAA plassert i scenarioet for demo-atferd.",
        "guide.control.5": "<b>Simulator:</b> injiserer, redigerer, sletter eller manusstyrer enhetsatferd.",
        "guide.control.6": "<b>Briefing:</b> genererer en lesbar forklaring av den nåværende anbefalingen.",
        "guide.steps_title": "Trinn for trinn",
        "guide.steps.1": "Åpne dette dashbordet og velg et scenario i toppmenyen.",
        "guide.steps.2": "Trykk <b>Start</b>. Motoren begynner å fremdrift og situasjonen utvikler seg.",
        "guide.steps.3": "Observer kartet til venstre og <b>Trussel</b>-indikatoren i toppfeltet. Hvis den hopper til HØY eller KRITISK, har analysen oppdaget en relevant endring.",
        "guide.steps.4": "Åpne <b>Kontakter</b> for å se aktive enheter og varselsflagg.",
        "guide.steps.5": "Åpne <b>COAer</b> for å gjennomgå klassifiserte alternativer. Hvis det finnes en koordinert pakke, vises den over de individuelle COAene.",
        "guide.steps.6": "Åpne <b>Simulator</b> hvis du vil plassere en ny enhet på kartet eller tvinge frem en manøver, interferens eller tilnærming.",
        "guide.steps.7": "Trykk <b>Generer briefing</b> når du ønsker en konsis operasjonell oppsummering.",
        "guide.callout.major_change": "Hva teller som en viktig endring?",
        "guide.callout.major_change.text": "Eksempler: et skip svinger mot infrastruktur, patruljerer nær en kabel, en UAV dukker opp nær flyplassen, interferens sendes ut eller den anbefalte COA endres.",
        "guide.callout.bundle_q": "Hva er en pakke?",
        "guide.callout.bundle_a": "En pakke er rett og slett flere rådgivende COAer som gir mening sammen, for eksempel skygge + ISR + kabelbeskyttelse. Det er ikke en separat eller mystisk modus.",
        "guide.callout.not_doing": "Hva systemet ikke gjør:",
        "guide.callout.not_doing.text": "utfører ikke ordre, tildeler ikke våpen og autoriserer ikke engasjement autonomt.",
        "contacts.stat.contacts": "Kontakter",
        "contacts.stat.tracks": "Spor",
        "contacts.stat.coas": "COAer",
        "contacts.stat.processed": "Behandlet",
        "briefing.generate": "Generer briefing",
        "briefing.download_pdf": "Last ned PDF",
        "briefing.download_pdf_en": "Last ned PDF (EN)",
        "sim.quick_scenarios": "Raske scenarioer",
        "sim.quick_desc": "Bruk disse forhåndsinnstillingene hvis du vil at motoren skal reagere synlig. Fiendtlige og ukjente kontakter øker presset. Alliert patrulje og ISR forbedrer tilgjengelig støtte og kan låse opp sterkere koordinerte pakker.",
        "sim.play.maritime_threat": "Maritim trussel nær kabel",
        "sim.play.maritime_threat.desc": "Injisere et fiendtlig skip nær infrastruktur med slått av AIS og mistenkelig lav hastighet",
        "sim.play.uav_airport": "UAV nær flyplass",
        "sim.play.uav_airport.desc": "Injisere en fiendtlig UAV med luftromrisikosignatur",
        "sim.play.ew_escalation": "EW-eskalering",
        "sim.play.ew_escalation.desc": "Injisere en interferenskilde i det nåværende operasjonsområdet",
        "sim.play.allied_isr": "Legg til alliert ISR-støtte",
        "sim.play.allied_isr.desc": "Injisere en vennlig UAV/støtteaktiv for å teste posisjonsendringer",
        "sim.play.allied_patrol": "Legg til alliert patrulje",
        "sim.play.allied_patrol.desc": "Injisere et alliert patruljeskip i sonen",
        "sim.play.cable_alert": "Infrastrukturhendelse",
        "sim.play.cable_alert.desc": "Injisere en kabelhendelsesvarsel nær kartets sentrum",
        "sim.undo_last": "Angre siste injeksjon",
        "sim.reset_scenario": "Tilbakestill scenario",
        "sim.preset.suspicious_vessel": "Mistenkelig fartøy",
        "sim.preset.suspicious_vessel.desc": "Fiendtlig skip nær kartets nåværende sentrum",
        "sim.preset.hostile_uav": "Fiendtlig UAV",
        "sim.preset.hostile_uav.desc": "UAV med forhøyet trussel-signatur",
        "sim.preset.jamming_event": "Interferenshendelse",
        "sim.preset.jamming_event.desc": "Injisere en interferenskontakt som påvirker anomalier",
        "sim.preset.cable_event": "Kabelhendelse",
        "sim.preset.cable_event.desc": "Injisere en kabelbrudd-lignende hendelse",
        "sim.quick.add_suspicious": "Legg til mistenkelig skip nå",
        "sim.quick.add_suspicious.desc": "Umiddelbar fiendtlig maritim kontakt i kartets sentrum",
        "sim.quick.add_uav": "Legg til fiendtlig UAV nå",
        "sim.quick.add_uav.desc": "Umiddelbar luftkontakt nær det nåværende området",
        "sim.quick.trigger_jamming": "Aktiver interferens nå",
        "sim.quick.trigger_jamming.desc": "Umiddelbar EW-anomali i det nåværende området",
        "sim.quick.trigger_cable": "Aktiver kabelvarsel nå",
        "sim.quick.trigger_cable.desc": "Umiddelbar infrastrukturhendelse nær kartets sentrum",
        "sim.show_advanced": "Vis avansert plassering",
        "sim.form.name": "Navn",
        "sim.form.type": "Type",
        "sim.form.allegiance": "Tilhørighet",
        "sim.form.speed": "Hastighet (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Breddegrad",
        "sim.form.longitude": "Lengdegrad",
        "sim.form.jamming_radius": "Interferensradius (mn)",
        "sim.form.ais_off": "AIS av",
        "sim.form.position": "Posisjon",
        "sim.form.add_unit": "Legg til enhet",
        "sim.form.cancel": "Avbryt",
        "sim.option.vessel": "Skip",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Ubåt",
        "sim.option.convoy": "Konvoi",
        "sim.option.jamming": "Interferens",
        "sim.option.cable_event": "Kabelhendelse",
        "sim.option.hostile": "Fiendtlig",
        "sim.option.friendly": "Alliert",
        "sim.option.neutral": "Nøytral"
    },
    "is": {
        "header.badge.disconnected": "Engjalið",
        "header.threat": "Hætta",
        "scenario.baltic": "Báltahaf",
        "scenario.arctic": "Arktískur",
        "scenario.mediterranean": "Miðjuharhaf",
        "btn.start": "Upphafa",
        "btn.stop": "Haltar",
        "subheader.what": "Hvað er þetta:",
        "subheader.what.text": "live ákvörðunarstúkan í bakgrunni sem tekur inn syntetískan stafræðar, uppfærir hættustig, skapar ráðgjaflegar COA, simuleirar niðurstöður og ráðgerir pakka.",
        "guide.step1": "1. Veldu svið",
        "guide.step2": "2. Smelltu á Upphafa",
        "guide.step3": "3. Athuga hvernig stafræðar og hætta breytast",
        "guide.step4": "4. Skoða COA / pakka",
        "guide.step5": "5. Nota Simulatorkennsluna til að innjósa eða breyta einingum",
        "guide.step6": "6. Skapa samantekt",
        "why.changed": "Hvað breyttist",
        "map.style": "Kartastíll",
        "map.style.osm_standard": "Standard OSM",
        "map.style.osm_humanitarian": "OSM mannréttindi",
        "map.style.carto_light": "Carto ljós",
        "map.style.carto_dark": "Carto myrk",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Skoða einingar",
        "map.filter.friendly": "Samstarfsaðilar",
        "map.filter.hostile": "Fiðingar",
        "map.filter.neutral": "Hlutlausar",
        "map.filter.air": "Flug",
        "map.filter.naval": "Sjó",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastruktúr",
        "map.filter.cable_routes": "Skoða kebla leiðir",
        "map.filter.noaa_traffic": "Skoða NOAA replay",
        "tab.guide": "Leiðbeiningar",
        "tab.contacts": "Stafræðar",
        "tab.coas": "COA",
        "tab.briefing": "Samantekt",
        "tab.simulator": "Simulatur",
        "tab.log": "Dagbók",
        "guide.how_title": "Hvernig kerfið virkar",
        "guide.how.1": "Vélinn sendir eða tekur við stafræðum eins og skip, UAV, störfunar störfunar og kebla hendingar.",
        "guide.how.2": "Hver nýr stafræður uppfærir live staðreyndir og stafræðahistoríu.",
        "guide.how.3": "Greininghlúpan reiknar út anomalíviðvörunir og hættumögel til hverrar einingar.",
        "guide.how.4": "COA vélinn skapar valkostir byggt á reglunum. Hún leyfir ekki LLM að kynna upp aðgerðir.",
        "guide.how.5": "Hver COA er simuleirat og skoðað. Eftir það athugar skipulagari hvort samræmt pakka af fleiri COA sé raunverulega mögulegt með núverandi miðlum.",
        "guide.how.6": "Kerfið undirstrikar besta ráðgjöfina og getur skapað samantekt í stíl stjórnanda eftir beiðni.",
        "guide.control_title": "Hvað þú stýrir",
        "guide.control.1": "<b>Svið:</b> veldu syntetískt starfsgeirinn og skráðan þróun hættunnar.",
        "guide.control.2": "<b>Upphafa / Haltar:</b> upphafar eða heldur live tick-hlúpan.",
        "guide.control.3": "<b>Kartinn:</b> vinstri hliðin sýnir alltaf núverandi mynd stafræðar.",
        "guide.control.4": "<b>NOAA Replay Traffic:</b> valfrjáleg lagaflokkur af sögulegum AIS sporum NOAA sem er staðsett í sviðinu fyrir demo-hagstök.",
        "guide.control.5": "<b>Simulatur:</b> innjósar, breytir, fjarlegir eða skráar hagstökum eininga.",
        "guide.control.6": "<b>Samantekt:</b> skapar lesilega útskýringu á núverandi ráðgjöf. ",
        "guide.steps_title": "Stig fyrir stig",
        "guide.steps.1": "Opna þetta dashboard og veldu svið í yfirborði.",
        "guide.steps.2": "Smelltu á <b>Upphafa</b>. Vélinn byrjar að framleiða og tilfinningin þróast.",
        "guide.steps.3": "Athuga kartinn til vinstri og hættustig í yfirborði. Ef það hoppar til HÁTT eða KRÍTÍSKT, hefur greiningin séð mikilvæga breytingu.",
        "guide.steps.4": "Opna <b>Stafræðar</b> til að sjá virkar einingar og varðvörunarsignalar.",
        "guide.steps.5": "Opna <b>COA</b> til að skoða flokkuð valkostir. Ef það er samræmt pakka, kemur það yfir einstaka COA.",
        "guide.steps.6": "Opna <b>Simulatur</b> ef þú vilt setja nýja einingu á kartann eða taka í forgang að manœbra, störfun eða nálgun.",
        "guide.steps.7": "Smelltu á <b>Skapa samantekt</b> þegar þú vilt stuttar starfsleg samantekt.",
        "guide.callout.major_change": "Hvað telst vera mikilvæg breyting?",
        "guide.callout.major_change.text": "Dæmi: skip snýr sig að infrastruktúru, fer í nálægð kebla, UAV kemur nálægt sjógaflutningsmiðstöðu, störfun er send eða COA er breytt.",
        "guide.callout.bundle_q": "Hvað er pakka?",
        "guide.callout.bundle_a": "Pakka er einfaldlega fleir ráðgjaflegar COA sem hafa meining saman, t.d. skuggi + ISR + kebla vernd. Það er ekki sérstakður aðgerðarstíl eða misgerð.",
        "guide.callout.not_doing": "Það sem kerfið gerir ekki:",
        "guide.callout.not_doing.text": "það framkvæmir ekki ábyrgðir, neyter ekki vopn og leyfir ekki sjálfvirka árásar.",
        "contacts.stat.contacts": "Stafræðar",
        "contacts.stat.tracks": "Spor",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Vinnuð",
        "briefing.generate": "Skapa samantekt",
        "briefing.download_pdf": "Hlaða niður PDF",
        "briefing.download_pdf_en": "Hlaða niður PDF (EN)",
        "sim.quick_scenarios": "Hraðsvið",
        "sim.quick_desc": "Notaðu þessi fyrirvara ef þú vilt að vélinn áhrifið sé sýnileg. Fiðingar og óþekktir stafræðar hækka álagið. Samstarfsaðilar og ISR bæta við tilgjengilegum stuðningi og geta opnað sterkari samræmta pakka.",
        "sim.play.maritime_threat": "Sjóhætta nálægt kebla",
        "sim.play.maritime_threat.desc": "Innjósar fiðingi skip nálægt infrastruktúru með AIS slokað og mistökum hagstökum við lágri hraða",
        "sim.play.uav_airport": "UAV nálægt sjógaflutningsmiðstöðu",
        "sim.play.uav_airport.desc": "Innjósar fiðingi UAV með fluggeirsáhættusignali",
        "sim.play.ew_escalation": "EW aukning",
        "sim.play.ew_escalation.desc": "Innjósar störfunar störfunar killa í núverandi starfsgeirinu",
        "sim.play.allied_isr": "Bæta við samstarfsaðila ISR",
        "sim.play.allied_isr.desc": "Innjósar samstarfsaðila UAV/stuðningsaktiv til að prófa stöðugleika breytinga",
        "sim.play.allied_patrol": "Bæta við samstarfsaðila patrullu",
        "sim.play.allied_patrol.desc": "Innjósar samstarfsaðila patrullskip í svæðið",
        "sim.play.cable_alert": "Infrastruktúru hending",
        "sim.play.cable_alert.desc": "Innjósar kebla hendingu eins og hending kebla nálægt miðju kartans",
        "sim.undo_last": "Endurhaga síðasta innjósi",
        "sim.reset_scenario": "Endursetja svið",
        "sim.preset.suspicious_vessel": "Miskilvægt skip",
        "sim.preset.suspicious_vessel.desc": "Fiðingi skip nálægt núverandi miðju kartans",
        "sim.preset.hostile_uav": "Fiðingi UAV",
        "sim.preset.hostile_uav.desc": "UAV með hækkað hættusignali",
        "sim.preset.jamming_event": "Störfunar störfunar hending",
        "sim.preset.jamming_event.desc": "Innjósar störfunar störfunar stafræðar sem áhrifar í anomalíum",
        "sim.preset.cable_event": "Kebla hending",
        "sim.preset.cable_event.desc": "Innjósar hendingu eins og kebla brot",
        "sim.quick.add_suspicious": "Bæta við miskilvægt skip núna",
        "sim.quick.add_suspicious.desc": "Strax fiðingi sjóstafræður í miðju kartans",
        "sim.quick.add_uav": "Bæta við fiðingi UAV núna",
        "sim.quick.add_uav.desc": "Strax flugstafræður nálægt núverandi svæði",
        "sim.quick.trigger_jamming": "Killa störfunar störfunar núna",
        "sim.quick.trigger_jamming.desc": "Strax EW anomalí í núverandi svæði",
        "sim.quick.trigger_cable": "Killa kebla varðvörun núna",
        "sim.quick.trigger_cable.desc": "Strax infrastruktúru hending nálægt miðju kartans",
        "sim.show_advanced": "Sýna háþróaða setningu",
        "sim.form.name": "Nafn",
        "sim.form.type": "Tegund",
        "sim.form.allegiance": "Samstarfsaðilinn",
        "sim.form.speed": "Hraði (kts)",
        "sim.form.heading": "Rumbo",
        "sim.form.latitude": "Latitúð",
        "sim.form.longitude": "Longitúð",
        "sim.form.jamming_radius": "Killa reiknaður (mn)",
        "sim.form.ais_off": "AIS slokað",
        "sim.form.position": "Staðsetning",
        "sim.form.add_unit": "Bæta við einingu",
        "sim.form.cancel": "Haltar",
        "sim.option.vessel": "Skip",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Undargönguskip",
        "sim.option.convoy": "Flokkur",
        "sim.option.jamming": "Killa",
        "sim.option.cable_event": "Kebla hending",
        "sim.option.hostile": "Fiðingi",
        "sim.option.friendly": "Samstarfsaðili",
        "sim.option.neutral": "Hlutlaus"
    },
    "fi": {
        "header.badge.disconnected": "Katkaistu",
        "header.threat": "Uhanala",
        "scenario.baltic": "Pohjanmeri",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Merenkeski",
        "btn.start": "Aloita",
        "btn.stop": "Pysäytä",
        "subheader.what": "Mitä tämä on:",
        "subheader.what.text": "reaaliaikainen päätöksentekoa tukeva ympäristö, joka vastaanottaa synteettisiä kontakteja, päivittää uhkatilan, luo neuvotteluvaihtoehtoja (COA), simuloi tuloksia ja suosittelee pakettia.",
        "guide.step1": "1. Valitse skenaario",
        "guide.step2": "2. Paina Aloita",
        "guide.step3": "3. Tarkkaile kontaktien ja uhan muuttumista",
        "guide.step4": "4. Tarkastele COA:ita / pakettia",
        "guide.step5": "5. Käytä Simulaattoria syöttääksesi tai muokataksesi yksiköitä",
        "guide.step6": "6. Luo tilannekuvaus (briefing)",
        "why.changed": "Mitä muuttui",
        "map.style": "Karttatyyli",
        "map.style.osm_standard": "OpenStreetMap standardi",
        "map.style.osm_humanitarian": "OSM humanitaarinen",
        "map.style.carto_light": "Carto vaalea",
        "map.style.carto_dark": "Carto tumma",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Suodata yksiköt",
        "map.filter.friendly": "Liittolaiset",
        "map.filter.hostile": "Viholliset",
        "map.filter.neutral": "Neutraalit",
        "map.filter.air": "Ilma",
        "map.filter.naval": "Laivasto",
        "map.filter.land": "Maa",
        "map.filter.infra": "Infrastruktuuri",
        "map.filter.cable_routes": "Näytä kaapelireitit",
        "map.filter.noaa_traffic": "Näytä NOAA-liikenne toisto",
        "tab.guide": "Opas",
        "tab.contacts": "Kontaktit",
        "tab.coas": "COA:t",
        "tab.briefing": "Tilannekuvaus",
        "tab.simulator": "Simulaattori",
        "tab.log": "Lokitiedot",
        "guide.how_title": "Miten järjestelmä toimii",
        "guide.how.1": "Moottori lähettää tai vastaanottaa kontakteja kuten aluksia, UAV:ita, häiriöraportteja ja kaapelitapahtumia.",
        "guide.how.2": "Jokainen uusi kontakti päivittää reaaliaikaisen tilan ja kontaktihistorian.",
        "guide.how.3": "Analyysisykli laskee uudelleen poikkeamaindikaattoreita ja uhkaprobisitetteja entiteettiä kohden.",
        "guide.how.4": "COA-moottori luo vaihtoehtoja sääntöjen perusteella. Se ei anna LLM:n keksiä toimia.",
        "guide.how.5": "Jokainen COA simuloidaan ja pisteytetään. Sitten allokaattori tarkistaa, onko koordinoitu paketti useista COA:sta todella toteutettavissa nykyisillä välineillä.",
        "guide.how.6": "Järjestelmä korostaa parhaan suosituksen ja voi luoda pyydettäessä komentajan tyylisen tilannekuvauksen.",
        "guide.control_title": "Mitä hallitset",
        "guide.control.1": "<b>Skenaario:</b> valitse synteettinen toiminta-alue ja skenaarioitu uhan kehitys.",
        "guide.control.2": "<b>Aloita / Pysäytä:</b> aloita tai pysäytä reaaliaikaisen tikkausjäljen sykli.",
        "guide.control.3": "<b>Kartta:</b> vasen puoli näyttää aina kontaktien nykyisen kuvan.",
        "guide.control.4": "<b>NOAA-liikenne toisto:</b> valinnainen kerros NOAA-AIS-historiallisista jäljistä, jotka on sijoitettu skenaarioon demo-käyttäytymisen vuoksi.",
        "guide.control.5": "<b>Simulaattori:</b> syöttää, muokkaa, poistaa tai skenaarioi yksiköiden käyttäytymistä.",
        "guide.control.6": "<b>Tilannekuvaus:</b> luo luettavan selityksen nykyisestä suosituksesta.",
        "guide.steps_title": "Vaihe vaiheelta",
        "guide.steps.1": "Avaa tämä kojelauta ja valitse skenaario yläpalkista.",
        "guide.steps.2": "Paina <b>Aloita</b>. Moottori alkaa edetä ja tilanne kehittyy.",
        "guide.steps.3": "Tarkkaile vasemmalla olevaa karttaa ja otsikkorivin <b>Uhanala</b>-indikaattoria. Jos se nousee KORKEAAN tai KRIITTIIKSEKSI, analyysi on havainnut merkittävän muutoksen.",
        "guide.steps.4": "Avaa <b>Kontaktit</b> nähdäksesi aktiiviset yksiköt ja hälytysliput.",
        "guide.steps.5": "Avaa <b>COA:t</b> tarkastellaksesi luokiteltuja vaihtoehtoja. Jos on koordinoitu paketti, se näkyy yksittäisten COA:iden päällä.",
        "guide.steps.6": "Avaa <b>Simulaattori</b> jos haluat sijoittaa uuden yksikön kartalle tai pakottaa manööverin, häiriön tai lähestymisen.",
        "guide.steps.7": "Paina <b>Luo tilannekuvaus</b> kun haluat tiiviin operatiivisen yhteenvedon.",
        "guide.callout.major_change": "Mitä lasketaan merkittäväksi muutokseksi?",
        "guide.callout.major_change.text": "Esimerkkejä: alus kääntyy infrastruktuuria kohti, se kiertää kaapelin lähellä, UAV ilmestyy lentokentän lähellä, häiriö lähetetään tai suositeltu COA muuttuu.",
        "guide.callout.bundle_q": "Mitä paketti on?",
        "guide.callout.bundle_a": "Paketti on yksinkertaisesti useita neuvotteluvaihtoehtoja (COA), jotka ovat järkeviä yhdessä, esimerkiksi varjo + ISR + kaapelisuojaus. Se ei ole erillinen tai mystinen tila.",
        "guide.callout.not_doing": "Mitä järjestelmä EI tee:",
        "guide.callout.not_doing.text": "se ei suorita käskyjä, ei jaa aseita eikä auktorisoi taisteluita itsenäisesti.",
        "contacts.stat.contacts": "Kontaktit",
        "contacts.stat.tracks": "Jäljet",
        "contacts.stat.coas": "COA:t",
        "contacts.stat.processed": "Käsiteltyjä",
        "briefing.generate": "Luo tilannekuvaus",
        "briefing.download_pdf": "Lataa PDF",
        "briefing.download_pdf_en": "Lataa PDF (EN)",
        "sim.quick_scenarios": "Nopeat skenaariot",
        "sim.quick_desc": "Käytä näitä esiasetuksia, jos haluat, että moottori reagoi näkyvästi. Vihaiset ja tuntemattomat kontaktit lisäävät painetta. Liittolaisten partiointi ja ISR parantavat saatavilla olevaa tukea ja voivat avata vahvempia koordinoituja paketteja.",
        "sim.play.maritime_threat": "Merellinen uhka kaapelin lähellä",
        "sim.play.maritime_threat.desc": "Syöttää vihamaisen aluksen infrastruktuurin lähelle AIS-pois päältä ja epäilyttävällä hitaalla käyttäytymisellä",
        "sim.play.uav_airport": "UAV lentokentän lähellä",
        "sim.play.uav_airport.desc": "Syöttää vihamaisen UAV:n ilmatilan riskiprofiililla",
        "sim.play.ew_escalation": "EW-eskalointi",
        "sim.play.ew_escalation.desc": "Syöttää häiriölähteen nykyiseen toiminta-alueeseen",
        "sim.play.allied_isr": "Lisää liittolaisten ISR-tukea",
        "sim.play.allied_isr.desc": "Syöttää liittolaisen UAV/tukiyksikön testaamaan asennon muutoksia",
        "sim.play.allied_patrol": "Lisää liittolaisten partiointia",
        "sim.play.allied_patrol.desc": "Syöttää liittolaisen partioalus aluetta",
        "sim.play.cable_alert": "Infrastruktuuritapahtuma",
        "sim.play.cable_alert.desc": "Syöttää kaapelitapahtumaa muistuttavan hälytyksen kartan keskustaan",
        "sim.undo_last": "Peruuta viimeisin syöttö",
        "sim.reset_scenario": "Nollaa skenaario",
        "sim.preset.suspicious_vessel": "Epäilyttävä alus",
        "sim.preset.suspicious_vessel.desc": "Vihollinen alus nykyisen kartan keskustan lähellä",
        "sim.preset.hostile_uav": "Vihollinen UAV",
        "sim.preset.hostile_uav.desc": "UAV korkealla uhkaprofiililla",
        "sim.preset.jamming_event": "Häiriötapahtuma",
        "sim.preset.jamming_event.desc": "Syöttää häiriökontaktin, joka vaikuttaa poikkeamiin",
        "sim.preset.cable_event": "Kaapelitapahtuma",
        "sim.preset.cable_event.desc": "Syöttää kaapelikatkoksen kaltaisen tapahtuman",
        "sim.quick.add_suspicious": "Lisää epäilyttävä alus nyt",
        "sim.quick.add_suspicious.desc": "Välitön vihamainen merikontakti kartan keskustassa",
        "sim.quick.add_uav": "Lisää vihamainen UAV nyt",
        "sim.quick.add_uav.desc": "Välitön ilmakontakti nykyisen alueen lähellä",
        "sim.quick.trigger_jamming": "Aktivoi häiriö nyt",
        "sim.quick.trigger_jamming.desc": "Välitön EW-tyyppinen poikkeama nykyisellä alueella",
        "sim.quick.trigger_cable": "Aktivoi kaapelihälytys nyt",
        "sim.quick.trigger_cable.desc": "Välitön infrastruktuuritapahtuma kartan keskustassa",
        "sim.show_advanced": "Näytä edistynyt sijoittelu",
        "sim.form.name": "Nimi",
        "sim.form.type": "Tyyppi",
        "sim.form.allegiance": "Affiliaatio",
        "sim.form.speed": "Nopeus (kts)",
        "sim.form.heading": "Suunta",
        "sim.form.latitude": "Leveysaste",
        "sim.form.longitude": "Pituusaste",
        "sim.form.jamming_radius": "Häiriöalue (mn)",
        "sim.form.ais_off": "AIS pois päältä",
        "sim.form.position": "Sijainti",
        "sim.form.add_unit": "Lisää yksikkö",
        "sim.form.cancel": "Peruuta",
        "sim.option.vessel": "Alus",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Undervesi",
        "sim.option.convoy": "Konvoo",
        "sim.option.jamming": "Häiriö",
        "sim.option.cable_event": "Kaapelitapahtuma",
        "sim.option.hostile": "Vihamainen",
        "sim.option.friendly": "Liittolainen",
        "sim.option.neutral": "Neutraali"
    },
    "sv": {
        "header.badge.disconnected": "Avstängd",
        "header.threat": "Hot",
        "scenario.baltic": "Östersjön",
        "scenario.arctic": "Arktis",
        "scenario.mediterranean": "Medelhavet",
        "btn.start": "Starta",
        "btn.stop": "Stoppa",
        "subheader.what": "Vad är detta:",
        "subheader.what.text": "en live beslutsstödsmiljö som tar emot syntetiska kontakter, uppdaterar hotstatus, genererar konsultativa COA:er, simulerar resultat och rekommenderar ett paket.",
        "guide.step1": "1. Välj scenario",
        "guide.step2": "2. Tryck på Starta",
        "guide.step3": "3. Observera hur kontakter och hot ändras",
        "guide.step4": "4. Granska COA:er / paket",
        "guide.step5": "5. Använd Simuleringen för att injicera eller redigera enheter",
        "guide.step6": "6. Generera briefing",
        "why.changed": "Vad ändrades",
        "map.style": "Karta stil",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM humanitär",
        "map.style.carto_light": "Carto ljus",
        "map.style.carto_dark": "Carto mörk",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtrera enheter",
        "map.filter.friendly": "Vänner",
        "map.filter.hostile": "Fiender",
        "map.filter.neutral": "Neutrala",
        "map.filter.air": "Flyg",
        "map.filter.naval": "Marina",
        "map.filter.land": "Land",
        "map.filter.infra": "Infrastruktur",
        "map.filter.cable_routes": "Visa kabellinjer",
        "map.filter.noaa_traffic": "Visa NOAA-trafik replay",
        "tab.guide": "Guide",
        "tab.contacts": "Kontakter",
        "tab.coas": "COA:er",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Logg",
        "guide.how_title": "Hur systemet fungerar",
        "guide.how.1": "Motorn sänder eller tar emot kontakter som fartyg, UAV, störningsrapporter och kabelevent.",
        "guide.how.2": "Varje nytt kontakt uppdaterar live-statusen och kontakthistoriken.",
        "guide.how.3": "Analysloopen omberäknar anomalindikatorer och hotprocent per enhet.",
        "guide.how.4": "COA-motorn genererar alternativ baserat på regler. Den tillåter inte LLM att uppfinna handlingar.",
        "guide.how.5": "Varje COA simuleras och poängsätts. Därefter kontrollerar tilldelaren om ett koordinerat paket av flera COA:er är verkligen genomförbart med de nuvarande medlen.",
        "guide.how.6": "Systemet framhäver bästa rekommendationen och kan generera en kommandostil briefing på begäran.",
        "guide.control_title": "Vad du kontrollerar",
        "guide.control.1": "<b>Scenario:</b> väljer den syntetiska operationsområdet och den manusstyrda hotutvecklingen.",
        "guide.control.2": "<b>Starta / Stoppa:</b> startar eller stoppar live tick-loopen.",
        "guide.control.3": "<b>Karta:</b> vänster sida visar alltid den aktuella kontaktbilden.",
        "guide.control.4": "<b>NOAA Trafik Replay:</b> valfri lager av historiska AIS-spår från NOAA omplacerade i scenariot för demo-beteende.",
        "guide.control.5": "<b>Simulator:</b> injicerar, redigerar, tar bort eller manusstyrer enhetsbeteende.",
        "guide.control.6": "<b>Briefing:</b> genererar en läsbar förklaring av den aktuella rekommendationen.",
        "guide.steps_title": "Steg för steg",
        "guide.steps.1": "Öppna denna dashboard och välj ett scenario i toppfältet.",
        "guide.steps.2": "Tryck på <b>Starta</b>. Motorn börjar avancera och situationen utvecklas.",
        "guide.steps.3": "Observera kartan till vänster och <b>Hot</b>-indikatorn i rubriken. Om den hoppar till HÖG eller KRITISK har analysen upptäckt en relevant förändring.",
        "guide.steps.4": "Öppna <b>Kontakter</b> för att se aktiva enheter och varningsflaggor.",
        "guide.steps.5": "Öppna <b>COA:er</b> för att granska klassificerade alternativ. Om ett koordinerat paket finns, visas det ovanför de individuella COA:erna.",
        "guide.steps.6": "Öppna <b>Simulator</b> om du vill placera en ny enhet på kartan eller tvinga fram en manöver, störning eller ankomst.",
        "guide.steps.7": "Tryck på <b>Generera briefing</b> när du vill ha en koncis operativ sammanfattning.",
        "guide.callout.major_change": "Vad räknas som en stor förändring?",
        "guide.callout.major_change.text": "Exempel: ett fartyg svänger mot infrastruktur, patrullerar nära en kabel, en UAV dyker upp nära flygplatsen, en störning sänds ut eller den rekommenderade COA:n ändras.",
        "guide.callout.bundle_q": "Vad är ett paket?",
        "guide.callout.bundle_a": "Ett paket är helt enkelt flera konsultativa COA:er som går ihop, till exempel skugga + ISR + kabelskydd. Det är inte ett separat eller mystiskt läge.",
        "guide.callout.not_doing": "Vad systemet inte gör:",
        "guide.callout.not_doing.text": "utför inte order, tilldelar inte vapen och auktoriserar inte strider autonomt.",
        "contacts.stat.contacts": "Kontakter",
        "contacts.stat.tracks": "Spår",
        "contacts.stat.coas": "COA:er",
        "contacts.stat.processed": "Bearbetade",
        "briefing.generate": "Generera briefing",
        "briefing.download_pdf": "Ladda ner PDF",
        "briefing.download_pdf_en": "Ladda ner PDF (EN)",
        "sim.quick_scenarios": "Snabba scenarier",
        "sim.quick_desc": "Använd dessa förinställningar om du vill att motorn ska reagera synligt. Fiendeliga och okända kontakter ökar trycket. Vänlig patrull och ISR förbättrar tillgängligt stöd och kan låsa upp starkare koordinerade paket.",
        "sim.play.maritime_threat": "Maritimt hot nära kabeln",
        "sim.play.maritime_threat.desc": "Injektar ett fientligt fartyg nära infrastruktur med avstängt AIS och misstänkt låghastighetsbeteende",
        "sim.play.uav_airport": "UAV nära flygplatsen",
        "sim.play.uav_airport.desc": "Injektar en fientlig UAV med luftrumsrisksignatur",
        "sim.play.ew_escalation": "EW-eskalering",
        "sim.play.ew_escalation.desc": "Injektar en störningskälla i det aktuella operationsområdet",
        "sim.play.allied_isr": "Lägg till vänligt ISR-stöd",
        "sim.play.allied_isr.desc": "Injektar en vänlig UAV/stödaktivitet för att testa posturförändringar",
        "sim.play.allied_patrol": "Lägg till vänlig patrull",
        "sim.play.allied_patrol.desc": "Injektar ett vänligt patrullfartyg i zonen",
        "sim.play.cable_alert": "Infrastrukturhändelse",
        "sim.play.cable_alert.desc": "Injektar en kabelhändelse-typ varning nära kartans mitt",
        "sim.undo_last": "Ångra senaste injektion",
        "sim.reset_scenario": "Återställ scenario",
        "sim.preset.suspicious_vessel": "Misstänkt fartyg",
        "sim.preset.suspicious_vessel.desc": "Fientligt fartyg nära kartans nuvarande mitt",
        "sim.preset.hostile_uav": "Fientlig UAV",
        "sim.preset.hostile_uav.desc": "UAV med högt hot-signatur",
        "sim.preset.jamming_event": "Störningshändelse",
        "sim.preset.jamming_event.desc": "Injektar en störningskontakt som påverkar anomalier",
        "sim.preset.cable_event": "Kabelevent",
        "sim.preset.cable_event.desc": "Injektar en kabelbrott-typ händelse",
        "sim.quick.add_suspicious": "Lägg till misstänkt fartyg nu",
        "sim.quick.add_suspicious.desc": "Omedelbar fientlig maritim kontakt i kartans mitt",
        "sim.quick.add_uav": "Lägg till fientlig UAV nu",
        "sim.quick.add_uav.desc": "Omedelbar luftkontakt nära det aktuella området",
        "sim.quick.trigger_jamming": "Aktivera störning nu",
        "sim.quick.trigger_jamming.desc": "Omedelbar EW-anomali i det aktuella området",
        "sim.quick.trigger_cable": "Aktivera kabelvarning nu",
        "sim.quick.trigger_cable.desc": "Omedelbar infrastrukturhändelse nära kartans mitt",
        "sim.show_advanced": "Visa avancerad placering",
        "sim.form.name": "Namn",
        "sim.form.type": "Typ",
        "sim.form.allegiance": "Tillhörighet",
        "sim.form.speed": "Hastighet (kts)",
        "sim.form.heading": "Riktning",
        "sim.form.latitude": "Latitud",
        "sim.form.longitude": "Longitud",
        "sim.form.jamming_radius": "Störningsradie (mn)",
        "sim.form.ais_off": "AIS avstängt",
        "sim.form.position": "Position",
        "sim.form.add_unit": "Lägg till enhet",
        "sim.form.cancel": "Avbryt",
        "sim.option.vessel": "Fartyg",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Ubåt",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Störning",
        "sim.option.cable_event": "Kabelevent",
        "sim.option.hostile": "Fientlig",
        "sim.option.friendly": "Vänlig",
        "sim.option.neutral": "Neutral"
    },
    "sq": {
        "header.badge.disconnected": "Ndezaktivizuar",
        "header.threat": "Kërcënim",
        "scenario.baltic": "Deti Baltik",
        "scenario.arctic": "Arktiku",
        "scenario.mediterranean": "Deti Mesditeran",
        "btn.start": "Filloni",
        "btn.stop": "Ndërprisni",
        "subheader.what": "Çfarë është kjo:",
        "subheader.what.text": "një mjedis mbështetës vendimmarrjeje në kohë reale që thith kontakte sintetikë, përditëson statusin e kërcënimit, gjeneron COA-të konsultative, simulon rezultatet dhe rekomandon një paketë.",
        "guide.step1": "1. Zgjidhni skenarin",
        "guide.step2": "2. Shtypni Filloni",
        "guide.step3": "3. Vëzhgoni si ndryshojnë kontaktet dhe kërcënimi",
        "guide.step4": "4. Rishikoni COA-të / paketën",
        "guide.step5": "5. Përdorni Simulatorin për të injektuar ose redaktuar njësi",
        "guide.step6": "6. Gjeneroni briefing",
        "why.changed": "Çfarë ndryshoi",
        "map.style": "Stili i hartës",
        "map.style.osm_standard": "OpenStreetMap standard",
        "map.style.osm_humanitarian": "OSM humanitar",
        "map.style.carto_light": "Carto i lehtë",
        "map.style.carto_dark": "Carto i errët",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtroni njësi",
        "map.filter.friendly": "Aleatë",
        "map.filter.hostile": "Armiqë",
        "map.filter.neutral": "Neutrale",
        "map.filter.air": "Ajrore",
        "map.filter.naval": "Detare",
        "map.filter.land": "Brendëtokore",
        "map.filter.infra": "Infrastrukturë",
        "map.filter.cable_routes": "Shfaq rrugët e kabllove",
        "map.filter.noaa_traffic": "Shfaq ri-transmetimin NOAA të trafikut",
        "tab.guide": "Udhëzues",
        "tab.contacts": "Kontakte",
        "tab.coas": "COA-të",
        "tab.briefing": "Briefing",
        "tab.simulator": "Simulator",
        "tab.log": "Regjistrim",
        "guide.how_title": "Si funksionon sistemi",
        "guide.how.1": "Motori lëshon ose merr kontakte si anije, UAV, raporte interferencë dhe ngjarje kablli.",
        "guide.how.2": "Çdo kontakt i ri përditëson statusin në kohë reale dhe historikun e kontakteve.",
        "guide.how.3": "Cikli i analizës rirrecionon treguesit e anomalive dhe probabilitetë e kërcënimit për çdo entitet.",
        "guide.how.4": "Motori i COA gjeneron opsione bazuar në rregulla. Nuk lejon LLM-in të shpikë veprime.",
        "guide.how.5": "Çdo COA simulohet dhe vlerësohet. Më pas, caktuesi kontrollon nëse një paketë koordinuar e disa COA-ve është vërtet e realizueshme me mjetet aktuale.",
        "guide.how.6": "Sistemi thekson rekomandimin më të mirë dhe mund të gjenerojë një briefing stili komandanti sipas kërkesës.",
        "guide.control_title": "Çfarë kontrolloni",
        "guide.control.1": "<b>Skenari:</b> zgjidhni zonën operative sintetikë dhe evolucionin e skenarit të kërcënimit.",
        "guide.control.2": "<b>Filloni / Ndërprisni:</b> fillon ose ndërpres ciklin e tik-eve në kohë reale.",
        "guide.control.3": "<b>Harta:</b> anësia e majtë tregon gjithmonë imazhin aktual të kontakteve.",
        "guide.control.4": "<b>Ri-transmetimi NOAA i Trafikut:</b> shtresë opsionale e gjurmëve historike AIS të NOAA vendosur në skenarin për sjellje demo.",
        "guide.control.5": "<b>Simulatori:</b> injekton, redakton, fshin ose skenarizon sjelljen e njësisë.",
        "guide.control.6": "<b>Briefing:</b> gjeneron një shpjegim të lexueshëm të rekomandimit aktual.",
        "guide.steps_title": "Hapë pas hapi",
        "guide.steps.1": "Hapni këtë dashboard dhe zgjidhni një skenar në shiritin e sipërm.",
        "guide.steps.2": "Shtypni <b>Filloni</b>. Motori fillon të përparojë dhe situata evoluon.",
        "guide.steps.3": "Vëzhgoni hartën në majtas dhe treguesin e <b>Kërcënimit</b> në krye. Nëse shkon në TË LARTË ose TË KRITIKË, analiza ka zbuluar një ndryshim të rëndësishëm.",
        "guide.steps.4": "Hapni <b>Kontakte</b> për të parë njësi aktive dhe flamujë paralajmërimi.",
        "guide.steps.5": "Hapni <b>COA-të</b> për të rishikuar opsionet e klasifikuara. Nëse ekziston një paketë koordinuar, ajo shfaqet mbi COA-të individuale.",
        "guide.steps.6": "Hapni <b>Simulatorin</b> nëse dëshironi të vendosni një njësi të re në hartë ose të detyroni një manovër, interferencë ose afërsisje.",
        "guide.steps.7": "Shtypni <b>Gjenero briefing</b> kur dëshironi një përmbledhje operative të shkurtër.",
        "guide.callout.major_change": "Çfarë konsiderohet një ndryshim i rëndësishëm?",
        "guide.callout.major_change.text": "Shembuj: një anije kthehet drejt infrastrukturës, rrethon pranë një kablli, shfaqet një UAV pranë aeroportit, lëshohet një interferencë ose ndryshon COA-ja e rekomanduar.",
        "guide.callout.bundle_q": "Çfarë është një paketë?",
        "guide.callout.bundle_a": "Një paketë është thjesht disa COA-të konsultative që kanë kuptim së bashku, p.sh. hijesh + ISR + mbrojtje e kabllit. Nuk është një mod i veçantë apo misterioz.",
        "guide.callout.not_doing": "Ajo që sistemi nuk bën:",
        "guide.callout.not_doing.text": "nuk ekzekuton urdhëra, nuk caktuar armë dhe nuk autorizon përballje në mënyrë autonome.",
        "contacts.stat.contacts": "Kontakte",
        "contacts.stat.tracks": "Gjurmë",
        "contacts.stat.coas": "COA-të",
        "contacts.stat.processed": "Të përpunuar",
        "briefing.generate": "Gjenero briefing",
        "briefing.download_pdf": "Shkarko PDF",
        "briefing.download_pdf_en": "Shkarko PDF (EN)",
        "sim.quick_scenarios": "Skenare të shpejta",
        "sim.quick_desc": "Përdorni këto cilësime paraprake nëse dëshironi që motori të reagojë në mënyrë të dukshme. Kontaktet armiqë dhe të panjohura rrisin presionin. Patrulla dhe ISR-i aleatë përmirësojnë mbështetjen e disponueshme dhe mund të zhbllokojnë paketa koordinuara më të forta.",
        "sim.play.maritime_threat": "Kërcënim detar pranë kabllit",
        "sim.play.maritime_threat.desc": "Injekton një anije armiqë pranë infrastrukturës me AIS të fikur dhe sjellje të dyshimtë me shpejtësi të ulët",
        "sim.play.uav_airport": "UAV pranë aeroportit",
        "sim.play.uav_airport.desc": "Injekton një UAV armiq me shenjë rreziku të hapësirës ajrore",
        "sim.play.ew_escalation": "Eskalimi EW",
        "sim.play.ew_escalation.desc": "Injekton një burim interferencë në zonën operative aktuale",
        "sim.play.allied_isr": "Shto mbështetje ISR aleate",
        "sim.play.allied_isr.desc": "Injekton një UAV/aktiv mbështetës miq për të provuar ndryshime të pozicionit",
        "sim.play.allied_patrol": "Shto patrullë aleate",
        "sim.play.allied_patrol.desc": "Injekton një anije patrulluese aleate në zonë",
        "sim.play.cable_alert": "Incident infrastrukturë",
        "sim.play.cable_alert.desc": "Injekton një paralajmërim lloji ngjarje kablli pranë qendrës së hartës",
        "sim.undo_last": "Anulo injektimin e fundit",
        "sim.reset_scenario": "Rinis skenarin",
        "sim.preset.suspicious_vessel": "Anije e dyshimtë",
        "sim.preset.suspicious_vessel.desc": "Anije armiq pranë qendrës aktuale të hartës",
        "sim.preset.hostile_uav": "UAV armiq",
        "sim.preset.hostile_uav.desc": "UAV me shenjë kërcënimi të lartë",
        "sim.preset.jamming_event": "Ngjarje interferencë",
        "sim.preset.jamming_event.desc": "Injekton një kontakt interferencë që prek anomalitë",
        "sim.preset.cable_event": "Ngjarje kablli",
        "sim.preset.cable_event.desc": "Injekton një ngjarje lloji thyerje kablli",
        "sim.quick.add_suspicious": "Shto anije e dyshimtë tani",
        "sim.quick.add_suspicious.desc": "Kontakt detar armiq i menjëhershëm në qendrën e hartës",
        "sim.quick.add_uav": "Shto UAV armiq tani",
        "sim.quick.add_uav.desc": "Kontakt ajror i menjëhershëm pranë zonës aktuale",
        "sim.quick.trigger_jamming": "Aktivizo interferencë tani",
        "sim.quick.trigger_jamming.desc": "Anomali lloji EW i menjëhershëm në zonën aktuale",
        "sim.quick.trigger_cable": "Aktivizo paralajmërim kablli tani",
        "sim.quick.trigger_cable.desc": "Incident infrastrukturë i menjëhershëm pranë qendrës së hartës",
        "sim.show_advanced": "Shfaq vendosjen e avancuar",
        "sim.form.name": "Emri",
        "sim.form.type": "Lloji",
        "sim.form.allegiance": "Afiliacioni",
        "sim.form.speed": "Shpejtësia (kts)",
        "sim.form.heading": "Rumi",
        "sim.form.latitude": "Gjerësia",
        "sim.form.longitude": "Gjatësia",
        "sim.form.jamming_radius": "Rrethi i interferencës (mn)",
        "sim.form.ais_off": "AIS i fikur",
        "sim.form.position": "Pozicioni",
        "sim.form.add_unit": "Shto njësi",
        "sim.form.cancel": "Anulo",
        "sim.option.vessel": "Anije",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Submarin",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferencë",
        "sim.option.cable_event": "Ngjarje kablli",
        "sim.option.hostile": "Armiq",
        "sim.option.friendly": "Aleatë",
        "sim.option.neutral": "Neutrale"
    },
    "mk": {
        "header.badge.disconnected": "Одвојен",
        "header.threat": "Загроза",
        "scenario.baltic": "Балтијско море",
        "scenario.arctic": "Арктика",
        "scenario.mediterranean": "Средиземно море",
        "btn.start": "Стартирај",
        "btn.stop": "Стопи",
        "subheader.what": "Што е ова:",
        "subheader.what.text": "живо окружување за поддршка на одлучување кое го внесува синтетичките контакти, го ажурира стаништето на загроза, генерира консултативни COA, симулира резултати и препорачува пакет.",
        "guide.step1": "1. Избери сценарио",
        "guide.step2": "2. Кликни Стартирај",
        "guide.step3": "3. Следи како се менуваат пријателите и загрозата",
        "guide.step4": "4. Прегледај COA / пакет",
        "guide.step5": "5. Користи го Симулаторот за да внесеш или уредиш единици",
        "guide.step6": "6. Генерирај брифинг",
        "why.changed": "Што се промени",
        "map.style": "Стил на мапа",
        "map.style.osm_standard": "Стандардна OSM",
        "map.style.osm_humanitarian": "Humanitarna OSM",
        "map.style.carto_light": "Carto Светла",
        "map.style.carto_dark": "Carto Темна",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Филтрирај единици",
        "map.filter.friendly": "Пријатели",
        "map.filter.hostile": "Непријатели",
        "map.filter.neutral": "Неутрални",
        "map.filter.air": "Воздушни",
        "map.filter.naval": "Морски",
        "map.filter.land": "Наземни",
        "map.filter.infra": "Инфраструктура",
        "map.filter.cable_routes": "Прикажи кабелски рути",
        "map.filter.noaa_traffic": "Прикажи NOAA трафик реплеј",
        "tab.guide": "Водич",
        "tab.contacts": "Контакти",
        "tab.coas": "COA",
        "tab.briefing": "Брифинг",
        "tab.simulator": "Симулатор",
        "tab.log": "Лог",
        "guide.how_title": "Како функционира системот",
        "guide.how.1": "Моторот испушта или прима контакти како брода, UAV, извештаи за интерференција и кабелски настани.",
        "guide.how.2": "Секој нов контакт го ажурира животот станиште и историјата на контактите.",
        "guide.how.3": "Циклусот на анализа го пресметува индикаторите на аномалии и веројатноста на загроза по ентитет.",
        "guide.how.4": "Моторот на COA генерира опции врз основа на правила. Не дозволува на LLM да измислува дејствија.",
        "guide.how.5": "Секој COA се симулира и оценува. Потоа асигнаторот проверува дали координиран пакет од повеќе COA е навистина изводилив со тековните средства.",
        "guide.how.6": "Системот ги истакнува најдобрите препораки и може да генерира брифинг на стил на командир на барање.",
        "guide.control_title": "Што контролираш",
        "guide.control.1": "<b>Сценарио:</b> изберете го синтетичкиот оперативен простор и сценариото на еволуција на загрозата.",
        "guide.control.2": "<b>Стартирај / Стопи:</b> започнува или го спира циклусот на животни тикови.",
        "guide.control.3": "<b>Мапа:</b> левата страна секогаш прикажува сличен преглед на контактите.",
        "guide.control.4": "<b>NOAA Трафик Реплеј:</b> опционален слој на историски AIS траги од NOAA поместени во сценариото за демо однесување.",
        "guide.control.5": "<b>Симулатор:</b> внесува, уредува, брише или сценаризира однесување на единиците.",
        "guide.control.6": "<b>Брифинг:</b> генерира разбирлив објаснување на тековната препорака.",
        "guide.steps_title": "Чекор по чекор",
        "guide.steps.1": "Отвори го овој дашборд и избери сценарио во горниот бар.",
        "guide.steps.2": "Кликни <b>Стартирај</b>. Моторот почнува да напредува и ситуацијата еволуира.",
        "guide.steps.3": "Следи ја мапата на левата страна и индикаторот за <b>Загроза</b> во главата. Ако скокне на ВИСОКА или КРИТИЧНА, анализата детектира релевантна промена.",
        "guide.steps.4": "Отвори <b>Контакти</b> за да видиш активни единици и сигнали за аларм.",
        "guide.steps.5": "Отвори <b>COA</b> за да прегледаш класифицирани опции. Ако постои координиран пакет, тој се појавува над индивидуалните COA.",
        "guide.steps.6": "Отвори <b>Симулатор</b> ако сакаш да ставиш нова единица на мапата или да принудиш маневрување, интерференција или приближување.",
        "guide.steps.7": "Кликни <b>Генерирај брифинг</b> кога сакаш концизен оперативен резиме.",
        "guide.callout.major_change": "Што се смета за значајна промена?",
        "guide.callout.major_change.text": "Примери: брода се свртува кон инфраструктура, патрулира блиску до кабел, се појавува UAV блиску до аеродромот, се испушта интерференција или се менува препорачаната COA.",
        "guide.callout.bundle_q": "Што е пакет?",
        "guide.callout.bundle_a": "Пакет е едноставно неколку консултативни COA кои имаат смисла заедно, на пример сенка + ISR + заштита на кабел. Не е одвоен или мистериозен режим.",
        "guide.callout.not_doing": "Што системот не прави:",
        "guide.callout.not_doing.text": "не ги извршува наредбите, не ги доделува оружјето и не овластува борби автономно.",
        "contacts.stat.contacts": "Контакти",
        "contacts.stat.tracks": "Траги",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Обработени",
        "briefing.generate": "Генерирај брифинг",
        "briefing.download_pdf": "Преземи PDF",
        "briefing.download_pdf_en": "Преземи PDF (EN)",
        "sim.quick_scenarios": "Брзи сценарија",
        "sim.quick_desc": "Користи ги овие пресеты ако сакаш моторот да реагира видливо. Непријателските и непознатите контакти го зголемуваат притисокот. Пријателската патрула и ISR подобруваат поддршка достапна и можат да ги отклучат посилни координирани пакети.",
        "sim.play.maritime_threat": "Морска загроза блиску до кабелот",
        "sim.play.maritime_threat.desc": "Внесува непријателска брода блиску до инфраструктура со исклучен AIS и сосомнително однесување на ниска брзина",
        "sim.play.uav_airport": "UAV блиску до аеродромот",
        "sim.play.uav_airport.desc": "Внесува непријателски UAV со сигнатура на ризик во воздушното простор",
        "sim.play.ew_escalation": "EW ескалација",
        "sim.play.ew_escalation.desc": "Внесува извор на интерференција во тековниот оперативен простор",
        "sim.play.allied_isr": "Додај пријателска ISR поддршка",
        "sim.play.allied_isr.desc": "Внесува пријателски UAV/актив на поддршка за тестирање на промени во позицијата",
        "sim.play.allied_patrol": "Додај пријателска патрула",
        "sim.play.allied_patrol.desc": "Внесува пријателска патрулна брода во зоната",
        "sim.play.cable_alert": "Инцидент со инфраструктура",
        "sim.play.cable_alert.desc": "Внесува аларм тип на кабелски настан блиску до центарот на мапата",
        "sim.undo_last": "Поврати последна инјекција",
        "sim.reset_scenario": "Ресетирај сценарио",
        "sim.preset.suspicious_vessel": "Сосомнителна брода",
        "sim.preset.suspicious_vessel.desc": "Непријателска брода блиску до тековниот центар на мапата",
        "sim.preset.hostile_uav": "Непријателски UAV",
        "sim.preset.hostile_uav.desc": "UAV со зголемена сигнатура на загроза",
        "sim.preset.jamming_event": "Настан на интерференција",
        "sim.preset.jamming_event.desc": "Внесува контакт на интерференција што влијае на аномалиите",
        "sim.preset.cable_event": "Кабелски настан",
        "sim.preset.cable_event.desc": "Внесува настан тип на прекин на кабел",
        "sim.quick.add_suspicious": "Додај сосомнителна брода сега",
        "sim.quick.add_suspicious.desc": "Имредјатен непријателски морски контакт во центарот на мапата",
        "sim.quick.add_uav": "Додај непријателски UAV сега",
        "sim.quick.add_uav.desc": "Имредјатен воздушен контакт блиску до тековната зона",
        "sim.quick.trigger_jamming": "Активирај интерференција сега",
        "sim.quick.trigger_jamming.desc": "Имредјатна EW аномалија во тековната зона",
        "sim.quick.trigger_cable": "Активирај кабелски аларм сега",
        "sim.quick.trigger_cable.desc": "Имредјатен инцидент со инфраструктура блиску до центарот на мапата",
        "sim.show_advanced": "Прикажи напредна позиција",
        "sim.form.name": "Име",
        "sim.form.type": "Тип",
        "sim.form.allegiance": "Припадност",
        "sim.form.speed": "Брзина (kts)",
        "sim.form.heading": "Курс",
        "sim.form.latitude": "Ширина",
        "sim.form.longitude": "Должина",
        "sim.form.jamming_radius": "Радиус на интерференција (mn)",
        "sim.form.ais_off": "AIS исклучен",
        "sim.form.position": "Позиција",
        "sim.form.add_unit": "Додај единица",
        "sim.form.cancel": "Откажи",
        "sim.option.vessel": "Брода",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Подводна брода",
        "sim.option.convoy": "Конвој",
        "sim.option.jamming": "Интерференција",
        "sim.option.cable_event": "Кабелски настан",
        "sim.option.hostile": "Непријателски",
        "sim.option.friendly": "Пријателски",
        "sim.option.neutral": "Неутрален"
    },
    "me": {
        "header.badge.disconnected": "Odvojen",
        "header.threat": "Pretnja",
        "scenario.baltic": "Baltički more",
        "scenario.arctic": "Arktik",
        "scenario.mediterranean": "Sredozemno more",
        "btn.start": "Pokreni",
        "btn.stop": "Zaustavi",
        "subheader.what": "Šta je ovo:",
        "subheader.what.text": "živo okruženje za podršku odlučivanju koje usisava sintetičke kontakte, ažurira status pretnje, generiše konsultativne COA-e, simulira rezultate i preporučuje paket.",
        "guide.step1": "1. Izaberi scenarij",
        "guide.step2": "2. Pritisni Pokreni",
        "guide.step3": "3. Posmatraj kako se kontakti i pretnja menjaju",
        "guide.step4": "4. Pregledaj COA / paket",
        "guide.step5": "5. Koristi Simulator za injektovanje ili uređivanje jedinica",
        "guide.step6": "6. Generiši brifing",
        "why.changed": "Šta se promenilo",
        "map.style": "Stil mape",
        "map.style.osm_standard": "Standardni OSM",
        "map.style.osm_humanitarian": "Humanitarni OSM",
        "map.style.carto_light": "Carto svetlo",
        "map.style.carto_dark": "Carto tamno",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Filtriraj jedinice",
        "map.filter.friendly": "Savezni",
        "map.filter.hostile": "Neprijateljski",
        "map.filter.neutral": "Neutralni",
        "map.filter.air": "Vazdušne",
        "map.filter.naval": "Morske",
        "map.filter.land": "Suhozemne",
        "map.filter.infra": "Infrastruktura",
        "map.filter.cable_routes": "Prikaži kabelske rute",
        "map.filter.noaa_traffic": "Prikaži NOAA replay saobraćaja",
        "tab.guide": "Vodič",
        "tab.contacts": "Kontakti",
        "tab.coas": "COA-e",
        "tab.briefing": "Brifing",
        "tab.simulator": "Simulator",
        "tab.log": "Dnevnik",
        "guide.how_title": "Kako sistem funkcioniše",
        "guide.how.1": "Motor emituje ili prima kontakte kao brodove, UAV, izveštaje o interferenciji i kabelske događaje.",
        "guide.how.2": "Svaki novi kontakt ažurira živi status i istoriju kontakata.",
        "guide.how.3": "Analitički ciklus ponovo izračunava indikatore anomalije i verovatnoće pretnje po entitetu.",
        "guide.how.4": "COA motor generiše opcije zasnovane na pravilima. Ne dozvoljava LLM-u da izmišlja akcije.",
        "guide.how.5": "Svaki COA se simulira i ocenjuje. Nakon toga, dodeljivač proverava da li je koordinisani paket više COA-a zaista izvodljiv sa trenutnim sredstvima.",
        "guide.how.6": "Sistem ističe najbolju preporuku i može generisati brifing tipa komandanta na zahtev.",
        "guide.control_title": "Šta kontrolišete",
        "guide.control.1": "<b>Scenarij:</b> odaberite sintetičku operativnu oblast i scenarijsku evoluciju pretnje.",
        "guide.control.2": "<b>Pokreni / Zaustavi:</b> pokreće ili zaustavlja živi ciklus tikova.",
        "guide.control.3": "<b>Mapa:</b> levi deo uvek prikazuje trenutnu sliku kontakata.",
        "guide.control.4": "<b>NOAA Replay Saobraćaj:</b> opcionalni sloj istorijskih AIS tragova NOAA-a premeštenih u scenarij za demo ponašanje.",
        "guide.control.5": "<b>Simulator:</b> injektuje, uređuje, briše ili scenariše ponašanje jedinica.",
        "guide.control.6": "<b>Brifing:</b> generiše čitljiv objašnjenje trenutne preporuke.",
        "guide.steps_title": "Korak po korak",
        "guide.steps.1": "Otvorite ovaj dashboard i izaberite scenarij u gornjem traci.",
        "guide.steps.2": "Pritisnite <b>Pokreni</b>. Motor počinje da napreduje i situacija se razvija.",
        "guide.steps.3": "Posmatrajte mapu na levoj strani i indikator <b>Pretnja</b> u zaglavlju. Ako skoči na VISOKU ili KRITIČNU, analiza je detektovala relevantnu promenu.",
        "guide.steps.4": "Otvorite <b>Kontakti</b> da vidite aktivne jedinice i alerte.",
        "guide.steps.5": "Otvorite <b>COA-e</b> da pregledate klasifikovane opcije. Ako postoji koordinisani paket, on se pojavljuje iznad pojedinačnih COA-a.",
        "guide.steps.6": "Otvorite <b>Simulator</b> ako želite da postavite novu jedinicu na mapu ili da prisilite manevar, interferenciju ili približavanje.",
        "guide.steps.7": "Pritisnite <b>Generiši brifing</b> kada želite sažet operativni pregled.",
        "guide.callout.major_change": "Šta se smatra značajnom promenom?",
        "guide.callout.major_change.text": "Primeri: brod okreće ka infrastrukturi, kruži blizu kabla, pojavljuje se UAV blizu aerodroma, emituje se interferencija ili se menja preporučena COA.",
        "guide.callout.bundle_q": "Šta je paket?",
        "guide.callout.bundle_a": "Paket je jednostavno više konsultativnih COA-a koje imaju smisla zajedno, npr. senka + ISR + zaštita kabla. Nije odvojen režim niti misterija.",
        "guide.callout.not_doing": "Šta sistem NE radi:",
        "guide.callout.not_doing.text": "ne izvršava naredbe, ne dodeljuje oružje i ne autorizuje sukobe autonomno.",
        "contacts.stat.contacts": "Kontakti",
        "contacts.stat.tracks": "Tragovi",
        "contacts.stat.coas": "COA-e",
        "contacts.stat.processed": "Obrađeno",
        "briefing.generate": "Generiši brifing",
        "briefing.download_pdf": "Preuzmi PDF",
        "briefing.download_pdf_en": "Preuzmi PDF (EN)",
        "sim.quick_scenarios": "Brzi scenariji",
        "sim.quick_desc": "Koristi ove predizborne postavke ako želiš da motor reaguje vidljivo. Neprijateljski i nepoznati kontakti povećavaju pritisak. Savezni patroli i ISR poboljšavaju dostupnu podršku i mogu otključati jače koordinisane pakete.",
        "sim.play.maritime_threat": "Morska pretnja blizu kabla",
        "sim.play.maritime_threat.desc": "Injektuje neprijateljski brod blizu infrastrukture sa isključenim AIS-om i sumnjivim ponašanjem na niskoj brzini",
        "sim.play.uav_airport": "UAV blizu aerodroma",
        "sim.play.uav_airport.desc": "Injektuje neprijateljski UAV sa signalom rizika za vazdušni prostor",
        "sim.play.ew_escalation": "EW eskalacija",
        "sim.play.ew_escalation.desc": "Injektuje izvor interferencije u trenutnoj operativnoj oblasti",
        "sim.play.allied_isr": "Dodaj savezni ISR podršku",
        "sim.play.allied_isr.desc": "Injektuje prijateljski UAV/aktiv za podršku za testiranje promena stava",
        "sim.play.allied_patrol": "Dodaj savezni patrol",
        "sim.play.allied_patrol.desc": "Injektuje savezni patrolni brod u zonu",
        "sim.play.cable_alert": "Inicijacija kabla",
        "sim.play.cable_alert.desc": "Injektuje alert tipa kabelski događaj blizu centra mape",
        "sim.undo_last": "Poništi poslednju injekciju",
        "sim.reset_scenario": "Resetuj scenarij",
        "sim.preset.suspicious_vessel": "Sumnjivi brod",
        "sim.preset.suspicious_vessel.desc": "Neprijateljski brod blizu trenutnog centra mape",
        "sim.preset.hostile_uav": "Neprijateljski UAV",
        "sim.preset.hostile_uav.desc": "UAV sa povišenim signalom pretnje",
        "sim.preset.jamming_event": "Događaj interferencije",
        "sim.preset.jamming_event.desc": "Injektuje kontakt interferencije koji utiče na anomalije",
        "sim.preset.cable_event": "Kabelski događaj",
        "sim.preset.cable_event.desc": "Injektuje događaj tipa kidanje kabla",
        "sim.quick.add_suspicious": "Dodaj sumnjivi brod sada",
        "sim.quick.add_suspicious.desc": "Odmah neprijateljski morski kontakt u centru mape",
        "sim.quick.add_uav": "Dodaj neprijateljski UAV sada",
        "sim.quick.add_uav.desc": "Odmah vazdušni kontakt blizu trenutne zone",
        "sim.quick.trigger_jamming": "Aktiviraj interferenciju sada",
        "sim.quick.trigger_jamming.desc": "Odmah EW anomalija u trenutnoj zoni",
        "sim.quick.trigger_cable": "Aktiviraj kabelski alert sada",
        "sim.quick.trigger_cable.desc": "Odmah kabelski incident blizu centra mape",
        "sim.show_advanced": "Prikaži napredno postavljanje",
        "sim.form.name": "Naziv",
        "sim.form.type": "Tip",
        "sim.form.allegiance": "Pripadnost",
        "sim.form.speed": "Brzina (kts)",
        "sim.form.heading": "Kurs",
        "sim.form.latitude": "Latituda",
        "sim.form.longitude": "Longituda",
        "sim.form.jamming_radius": "Radijus interferencije (mn)",
        "sim.form.ais_off": "AIS isključen",
        "sim.form.position": "Pozicija",
        "sim.form.add_unit": "Dodaj jedinicu",
        "sim.form.cancel": "Otkaži",
        "sim.option.vessel": "Brod",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Podmorski",
        "sim.option.convoy": "Konvoj",
        "sim.option.jamming": "Interferencija",
        "sim.option.cable_event": "Kabelski događaj",
        "sim.option.hostile": "Neprijateljski",
        "sim.option.friendly": "Savezni",
        "sim.option.neutral": "Neutralni"
    },
    "el": {
        "header.badge.disconnected": "Αποσυνδεδεμένο",
        "header.threat": "Απειλή",
        "scenario.baltic": "Βαλτικό Πέλαγος",
        "scenario.arctic": "Αρκτική",
        "scenario.mediterranean": "Μεσογειακό",
        "btn.start": "Έναρξη",
        "btn.stop": "Παύση",
        "subheader.what": "Τι είναι αυτό:",
        "subheader.what.text": "ένα περιβάλλον υποστήριξης αποφάσεων σε πραγματικό χρόνο που καταναλώνει συνθετικά ελέγχους, ενημερώνει την κατάσταση απειλής, παράγει συμβουλευτικές COA, προσομοιώνει αποτελέσματα και προτείνει ένα πακέτο.",
        "guide.step1": "1. Επιλογή σενάριου",
        "guide.step2": "2. Πατήστε Έναρξη",
        "guide.step3": "3. Παρατηρήστε την αλλαγή των ελέγχων και της απειλής",
        "guide.step4": "4. Εξέταση COA / πακέτου",
        "guide.step5": "5. Χρήση του Προσομοιωτή για εισαγωγή ή επεξεργασία μονάδων",
        "guide.step6": "6. Δημιουργία ενημέρωσης (briefing)",
        "why.changed": "Τι άλλαξε",
        "map.style": "Στυλ χάρτη",
        "map.style.osm_standard": "Standard OpenStreetMap",
        "map.style.osm_humanitarian": "Humanitarian OSM",
        "map.style.carto_light": "Carto Light",
        "map.style.carto_dark": "Carto Dark",
        "map.style.open_topo": "OpenTopoMap",
        "map.filter": "Φιλτράρισμα μονάδων",
        "map.filter.friendly": "Συμμαχικές",
        "map.filter.hostile": "Εχθρικές",
        "map.filter.neutral": "Ουδέτερες",
        "map.filter.air": "Αεροπορικές",
        "map.filter.naval": "Ναυτικές",
        "map.filter.land": "Γειτονικές",
        "map.filter.infra": "Υποδομές",
        "map.filter.cable_routes": "Εμφάνιση πορείας καλωδίων",
        "map.filter.noaa_traffic": "Εμφάνιση αναπαραγωγής NOAA traffic",
        "tab.guide": "Οδηγός",
        "tab.contacts": "Ελέγχοι",
        "tab.coas": "COA",
        "tab.briefing": "Ενημέρωση",
        "tab.simulator": "Προσομοιωτής",
        "tab.log": "Αρχείο καταγραφής",
        "guide.how_title": "Πώς λειτουργεί το σύστημα",
        "guide.how.1": "Ο κινητήρας εκπέμπει ή λαμβάνει ελέγχους ως πλοία, UAV, αναφορές παρεμβολής και συμβάντα καλωδίων.",
        "guide.how.2": "Κάθε νέος έλεγχος ενημερώνει την ζωντανή κατάσταση και το ιστορικό ελέγχων.",
        "guide.how.3": "Ο κύκλος ανάλυσης υπολογίζει ξανά δείκτες ανωμαλιών και πιθανότητες απειλής ανά οντότητα.",
        "guide.how.4": "Ο κινητήρας COA παράγει επιλογές με βάση κανόνες. Δεν επιτρέπει στο LLM να εφευρίσκει ενέργειες.",
        "guide.how.5": "Κάθε COA προσομοιώνεται και βαθμολογείται. Στη συνέχεια, ο εκχωρητής ελέγχει αν ένα συντονισμένο πακέτο πολλαπλών COA είναι πραγματικά εφικτό με τα τρέχοντα μέσα.",
        "guide.how.6": "Το σύστημα τονίζει την καλύτερη σύσταση και μπορεί να δημιουργήσει μια ενημέρωση τύπου διοικητή ανά ζήτηση.",
        "guide.control_title": "Τι ελέγχετε",
        "guide.control.1": "<b>Σενάριο:</b> επιλέγετε την συνθετική επιχειρησιακή περιοχή και την προγραμματισμένη εξέλιξη της απειλής.",
        "guide.control.2": "<b>Έναρξη / Παύση:</b> ξεκινά ή σταματά τον κύκλο ζωντανών ticks.",
        "guide.control.3": "<b>Χάρτης:</b> η αριστερή πλευρά δείχνει πάντα την τρέχουσα εικόνα των ελέγχων.",
        "guide.control.4": "<b>NOAA Replay Traffic:</b> προαιρετικό στρώμα ιστορικών ίχνη AIS της NOAA που μετατοπίζονται στο σενάριο για συμπεριφορά επίδемоνσης.",
        "guide.control.5": "<b>Προσομοιωτής:</b> εισάγει, επεξεργάζεται, διαγράφει ή προγραμματίζει τη συμπεριφορά των μονάδων.",
        "guide.control.6": "<b>Ενημέρωση:</b> δημιουργεί μια κατανοητή εξήγηση της τρέχουσας σύστασης.",
        "guide.steps_title": "Βήμα προς βήμα",
        "guide.steps.1": "Ανοίξτε αυτό το dashboard και επιλέξτε ένα σενάριο στην επάνω γραμμή.",
        "guide.steps.2": "Πατήστε <b>Έναρξη</b>. Ο κινητήρας αρχίζει να προχωρά και η κατάσταση εξελίσσεται.",
        "guide.steps.3": "Παρακολουθήστε τον χάρτη στα αριστερά και τον δείκτη <b>Απειλής</b> στην κεφαλίδα. Εάν ανέβει σε ΥΨΗΛΗ ή ΚΡΙΤΙΚΗ, η ανάλυση ανίχνευσε μια σχετική αλλαγή.",
        "guide.steps.4": "Ανοίξτε <b>Ελέγχοι</b> για να δείτε ενεργές μονάδες και σημεία συναγερμού.",
        "guide.steps.5": "Ανοίξτε <b>COA</b> για να δείτε τα κατηγοριοποιημένα επιλογές. Εάν υπάρχει ένα συντονισμένο πακέτο, εμφανίζεται πάνω από τις μεμονωμένες COA.",
        "guide.steps.6": "Ανοίξτε <b>Προσομοιωτής</b> αν θέλετε να τοποθετήσετε μια νέα μονάδα στον χάρτη ή να αναγκάσετε μια κίνηση, παρεμβολή ή προσέγγιση.",
        "guide.steps.7": "Πατήστε <b>Δημιουργία ενημέρωσης</b> όταν θέλετε μια συνοπτική επιχειρησιακή περίληψη.",
        "guide.callout.major_change": "Τι θεωρείται σημαντική αλλαγή;",
        "guide.callout.major_change.text": "Παραδείγματα: ένα πλοίο στρέφεται προς υποδομή, περιπλανιέται κοντά σε ένα καλώδιο, εμφανίζεται ένα UAV κοντά στο αεροδρόμιο, εκπέμπεται παρεμβολή ή αλλάζει η προτεινόμενη COA.",
        "guide.callout.bundle_q": "Τι είναι ένα πακέτο;",
        "guide.callout.bundle_a": "Ένα πακέτο είναι απλώς πολλαπλές συμβουλευτικές COA που έχουν νόημα μαζί, π.χ. σκιά + ISR + προστασία καλωδίου. Δεν είναι μια ξεχωριστή ή μυστηριώδης λειτουργία.",
        "guide.callout.not_doing": "Τι δεν κάνει το σύστημα:",
        "guide.callout.not_doing.text": "δεν εκτελεί εντολές, δεν εκχωρεί όπλα και δεν εξουσιοδοτεί μάχες αυτόνομα.",
        "contacts.stat.contacts": "Ελέγχοι",
        "contacts.stat.tracks": "Σχέδια",
        "contacts.stat.coas": "COA",
        "contacts.stat.processed": "Επεξεργασμένοι",
        "briefing.generate": "Δημιουργία ενημέρωσης",
        "briefing.download_pdf": "Λήψη PDF",
        "briefing.download_pdf_en": "Λήψη PDF (EN)",
        "sim.quick_scenarios": "Γρήγορα σενάρια",
        "sim.quick_desc": "Χρησιμοποιήστε αυτές τις προεπιλογές αν θέλετε ο κινητήρας να αντιδράει ορατά. Οι εχθρικοί και άγνωστοι έλεγχοι αυξάνουν την πίεση. Η συμμμαχική επιτήρηση και ISR βελτιώνουν την διαθέσιμη υποστήριξη και μπορούν να ξεκλειδώσουν ισχυρότερα συντονισμένα πακέτα.",
        "sim.play.maritime_threat": "Θαλάσσια απειλή κοντά στο καλώδιο",
        "sim.play.maritime_threat.desc": "Εισάγετε ένα εχθρικό πλοίο κοντά σε υποδομή με απενεργοποιημένο AIS και ύποπτη συμπεριφορά χαμηλής ταχύτητας",
        "sim.play.uav_airport": "UAV κοντά στο αεροδρόμιο",
        "sim.play.uav_airport.desc": "Εισάγετε ένα εχθρικό UAV με σήμα κινδύνου αεροπορικού χώρου",
        "sim.play.ew_escalation": "Εскаλάδα EW",
        "sim.play.ew_escalation.desc": "Εισάγετε μια πηγή παρεμβολής στην τρέχουσα επιχειρησιακή περιοχή",
        "sim.play.allied_isr": "Προσθήκη συμμμαχικής υποστήριξης ISR",
        "sim.play.allied_isr.desc": "Εισάγετε ένα συμμμαχικό UAV/υποστηρικτικό περιουσιακό στοιχείο για να δοκιμάσετε αλλαγές στάσης",
        "sim.play.allied_patrol": "Προσθήκη συμμμαχικής επιτήρησης",
        "sim.play.allied_patrol.desc": "Εισάγετε ένα συμμμαχικό πλοίο επιτήρησης στην περιοχή",
        "sim.play.cable_alert": "Συμβάντα υποδομής",
        "sim.play.cable_alert.desc": "Εισάγετε μια συναγερμό τύπου συμβάντος καλωδίου κοντά στο κέντρο του χάρτη",
        "sim.undo_last": "Ακύρωση τελευταίας εισαγωγής",
        "sim.reset_scenario": "Επαναφορά σε σενάριο",
        "sim.preset.suspicious_vessel": "Υποψιαίο πλοίο",
        "sim.preset.suspicious_vessel.desc": "Εχθρικό πλοίο κοντά στο τρέχον κέντρο του χάρτη",
        "sim.preset.hostile_uav": "Εχθρικό UAV",
        "sim.preset.hostile_uav.desc": "UAV με αυξημένο σήμα απειλής",
        "sim.preset.jamming_event": "Συμβάντα παρεμβολής",
        "sim.preset.jamming_event.desc": "Εισάγετε έναν έλεγχο παρεμβολής που επηρεάζει τις ανωμαλίες",
        "sim.preset.cable_event": "Συμβάντα καλωδίου",
        "sim.preset.cable_event.desc": "Εισάγετε ένα συμβάν τύπου διακοπής καλωδίου",
        "sim.quick.add_suspicious": "Προσθήκη υποψιαίου πλοίου τώρα",
        "sim.quick.add_suspicious.desc": "Άμεσος εχθρικός θαλάσσιος έλεγχος στο κέντρο του χάρτη",
        "sim.quick.add_uav": "Προσθήκη εχθρικού UAV τώρα",
        "sim.quick.add_uav.desc": "Άμεσος αεροπορικός έλεγχος κοντά στην τρέχουσα περιοχή",
        "sim.quick.trigger_jamming": "Ενεργοποίηση παρεμβολής τώρα",
        "sim.quick.trigger_jamming.desc": "Άμεση ανωμαλία τύπου EW στην τρέχουσα περιοχή",
        "sim.quick.trigger_cable": "Ενεργοποίηση συναγερμού καλωδίου τώρα",
        "sim.quick.trigger_cable.desc": "Άμεσο συμβάν υποδομής κοντά στο κέντρο του χάρτη",
        "sim.show_advanced": "Εμφάνιση προχωρημένης τοποθέτησης",
        "sim.form.name": "Όνομα",
        "sim.form.type": "Τύπος",
        "sim.form.allegiance": "Συμμαχία",
        "sim.form.speed": "Ταχύτητα (kts)",
        "sim.form.heading": "Κατεύθυνση",
        "sim.form.latitude": "Γεωγραφικό πλάτος",
        "sim.form.longitude": "Γεωγραφικό μήκος",
        "sim.form.jamming_radius": "Ακτίνα παρεμβολής (mn)",
        "sim.form.ais_off": "AIS απενεργοποιημένο",
        "sim.form.position": "Θέση",
        "sim.form.add_unit": "Προσθήκη μονάδας",
        "sim.form.cancel": "Ακύρωση",
        "sim.option.vessel": "Πλοίο",
        "sim.option.uav": "UAV",
        "sim.option.submarine": "Υποβρύχιο",
        "sim.option.convoy": "Συμμετοχή",
        "sim.option.jamming": "Παρεμβολή",
        "sim.option.cable_event": "Συμβάν καλωδίου",
        "sim.option.hostile": "Εχθρικό",
        "sim.option.friendly": "Συμμαχικό",
        "sim.option.neutral": "Ουδέτερο"
    }
}

COA_TEMPLATE_TRANSLATIONS: dict[str, dict[str, dict[str, object]]] = {
    "COA-TPL-ISR": {
        "en": {
            "title_template": "Increase ISR Coverage and Observation",
            "description_template": "Recommend increasing ISR coverage to maintain persistent observation of {entities}. Coordinate with available tactical UAV assets and satellite observation requests to improve coverage of the {infra} corridor.",
            "assumptions": [
                "ISR assets can be redirected within 30 minutes",
                "Weather permits UAV operations in the area",
                "Satellite revisit time is acceptable for tracking"
            ],
            "expected_effect_template": "Persistent observation of suspicious entities and {infra} corridor",
            "objective_template": "Maintain persistent awareness over {entities} and the {infra} corridor.",
            "rationale_template": "Selected because the situation requires better observation before higher-friction measures are considered."
        },
        "es": {
            "title_template": "Aumentar cobertura ISR y observación",
            "description_template": "Se recomienda aumentar la cobertura ISR para mantener observación persistente sobre {entities}. Coordinar con UAV tácticos disponibles y solicitudes de observación satelital para mejorar la cobertura del corredor de {infra}.",
            "assumptions": [
                "Los medios ISR pueden redirigirse en 30 minutos",
                "La meteorología permite operaciones UAV en la zona",
                "El tiempo de revisita satelital es aceptable para el seguimiento"
            ],
            "expected_effect_template": "Observación persistente de entidades sospechosas y del corredor de {infra}",
            "objective_template": "Mantener conocimiento persistente sobre {entities} y el corredor de {infra}.",
            "rationale_template": "Se selecciona porque la situación requiere mejor observación antes de considerar medidas de mayor fricción."
        },
        "fr": {
            "title_template": "Augmenter la Couverture et l'Observation ISR",
            "description_template": "Recommander d'augmenter la couverture ISR pour maintenir une observation persistante des {entities}. Coordonner avec les actifs de drones tactiques disponibles et les demandes d'observation par satellite pour améliorer la couverture du corridor {infra}.",
            "assumptions": [
                "Les actifs ISR peuvent être redirigés dans les 30 minutes",
                "La météo permet les opérations des drones dans la zone",
                "Le temps de revisite du satellite est acceptable pour le suivi"
            ],
            "expected_effect_template": "Observation persistante des entités suspectes et du corridor {infra}",
            "objective_template": "Maintenir une conscience persistante sur les {entities} et le corridor {infra}.",
            "rationale_template": "Sélectionné car la situation nécessite une meilleure observation avant que des mesures à friction plus élevée ne soient envisagées."
        },
        "de": {
            "title_template": "ISR-Abdeckung und Beobachtung erhöhen",
            "description_template": "Empfiehlt die Erhöhung der ISR-Abdeckung, um eine kontinuierliche Beobachtung von {entities} aufrechtzuerhalten. Koordiniert mit verfügbaren taktischen UAV-Assets und Satellitenbeobachtungsanfragen, um die Abdeckung des {infra}-Korridors zu verbessern.",
            "assumptions": [
                "ISR-Assets können innerhalb von 30 Minuten umgeleitet werden",
                "Das Wetter erlaubt UAV-Operationen in diesem Gebiet",
                "Die Satelliten-Wiederholzeit ist für die Verfolgung akzeptabel"
            ],
            "expected_effect_template": "Kontinuierliche Beobachtung verdächtiger Entitäten und des {infra}-Korridors",
            "objective_template": "Aufrechterhaltung der kontinuierlichen Wahrnehmung über {entities} und den {infra}-Korridor.",
            "rationale_template": "Ausgewählt, da die Situation eine bessere Beobachtung erfordert, bevor Maßnahmen mit höherer Reibung in Betracht gezogen werden."
        },
        "it": {
            "title_template": "Aumentare la Copertura ISR e l'Osservazione",
            "description_template": "Si raccomanda di aumentare la copertura ISR per mantenere un'osservazione persistente di {entities}. Coordinare con le risorse UAV tattiche disponibili e le richieste di osservazione satellitare per migliorare la copertura del corridoio {infra}.",
            "assumptions": [
                "Le risorse ISR possono essere reindirizzate entro 30 minuti",
                "Le condizioni meteorologiche consentono le operazioni UAV nell'area",
                "Il tempo di revisita satellitare è accettabile per il tracciamento"
            ],
            "expected_effect_template": "Osservazione persistente di entità sospette e del corridoio {infra}",
            "objective_template": "Mantenere una consapevolezza persistente su {entities} e sul corridoio {infra}.",
            "rationale_template": "Selezionato perché la situazione richiede una migliore osservazione prima di considerare misure a maggiore attrito."
        },
        "pt": {
            "title_template": "Aumentar a Cobertura e Observação de ISR",
            "description_template": "Recomenda-se aumentar a cobertura de ISR para manter a observação persistente de {entities}. Coordenar com os ativos táticos de UAV disponíveis e solicitações de observação por satélite para melhorar a cobertura do corredor {infra}.",
            "assumptions": [
                "Os ativos de ISR podem ser redirecionados em 30 minutos",
                "O clima permite operações de UAV na área",
                "O tempo de revisita do satélite é aceitável para rastreamento"
            ],
            "expected_effect_template": "Observação persistente de entidades suspeitas e corredor {infra}",
            "objective_template": "Manter consciência persistente sobre {entities} e o corredor {infra}.",
            "rationale_template": "Selecionado porque a situação requer melhor observação antes que medidas de maior fricção sejam consideradas."
        },
        "nl": {
            "title_template": "Verhoog ISR Dekking en Observatie",
            "description_template": "Aanbeveling om de ISR-dekking te verhogen om persistente observatie van {entities} te waarborgen. Coördineren met beschikbare tactische UAV-middelen en satellietobservatieverzoeken om de dekking van de {infra} corridor te verbeteren.",
            "assumptions": [
                "ISR-middelen kunnen binnen 30 minuten worden omgeleid",
                "Het weer staat UAV-operaties in het gebied toe",
                "De satelliet revisietijd is acceptabel voor tracking"
            ],
            "expected_effect_template": "Persistente observatie van verdachte entiteiten en de {infra} corridor",
            "objective_template": "Handhaven van persistente bewustwording over {entities} en de {infra} corridor.",
            "rationale_template": "Gekozen omdat de situatie betere observatie vereist voordat maatregelen met hogere wrijving worden overwogen."
        },
        "pl": {
            "title_template": "Zwiększenie Zasięgu ISR i Obserwacji",
            "description_template": "Rekomenduje się zwiększenie zasięgu ISR w celu utrzymania ciągłej obserwacji {entities}. Koordynacja z dostępnymi taktycznymi zasobami UAV i prośbami o obserwację satelitarną w celu poprawy pokrycia korytarza {infra}.",
            "assumptions": [
                "Zasoby ISR mogą zostać przekierowane w ciągu 30 minut",
                "Warunki pogodowe pozwalają na operacje UAV w danym obszarze",
                "Czas powrotu satelity jest akceptowalny do śledzenia"
            ],
            "expected_effect_template": "Ciągła obserwacja podejrzanych podmiotów i korytarza {infra}",
            "objective_template": "Utrzymanie ciągłej świadomości nad {entities} i korytarzem {infra}.",
            "rationale_template": "Wybrano, ponieważ sytuacja wymaga lepszej obserwacji, zanim rozważone zostaną środki o wyższym stopniu tarcia."
        },
        "tr": {
            "title_template": "ISR Kapsamını ve Gözlemi Artırın",
            "description_template": "{entities}'nın sürekli gözlemini sürdürmek için ISR kapsamının artırılmasını tavsiye eder. {infra} koridorunun kapsamını iyileştirmek için mevcut taktik UAV varlıkları ve uydu gözlem talepleri ile koordinasyon sağlayın.",
            "assumptions": [
                "ISR varlıkları 30 dakika içinde yeniden yönlendirilebilir",
                "Hava durumu bölgede UAV operasyonlarına izin veriyor",
                "Uydu tekrar ziyaret süresi takip için kabul edilebilir"
            ],
            "expected_effect_template": "Şüpheli varlıkların ve {infra} koridorunun sürekli gözlemlenmesi",
            "objective_template": "{entities} ve {infra} koridoru üzerinde sürekli farkındalık sürdürmek.",
            "rationale_template": "Seçildi çünkü durum, daha yüksek sürtünmeli önlemler düşünülmeden daha iyi gözlem gerektirmektedir."
        },
        "cs": {
            "title_template": "Zvýšit pokrytí a pozorování ISR",
            "description_template": "Doporučuje se zvýšit pokrytí ISR pro udržení trvalého pozorování {entities}. Koordinovat s dostupnými taktickými UAV prostředky a požadavky na satelitní pozorování pro zlepšení pokrytí koridoru {infra}.",
            "assumptions": [
                "ISR prostředky lze přesměrovat do 30 minut",
                "Počasí umožňuje provoz UAV v dané oblasti",
                "Čas opakování satelitu je přijatelný pro sledování"
            ],
            "expected_effect_template": "Trvalé pozorování podezřelých entit a koridoru {infra}",
            "objective_template": "Udržet trvalé povědomí o {entities} a koridoru {infra}.",
            "rationale_template": "Vybráno, protože situace vyžaduje lepší pozorování před zvážením opatření s vyšším třením."
        },
        "ro": {
            "title_template": "Creșterea Acoperirii și Observației ISR",
            "description_template": "Se recomandă creșterea acoperirii ISR pentru a menține observația persistentă a {entities}. Coordonați cu resursele UAV tactice disponibile și cererile de observație prin satelit pentru a îmbunătăți acoperirea coridorului {infra}.",
            "assumptions": [
                "Resursele ISR pot fi redirecționate în decurs de 30 de minute",
                "Vremea permite operațiunile UAV în zonă",
                "Timpul de revisitare a satelitului este acceptabil pentru urmărire"
            ],
            "expected_effect_template": "Observație persistentă a entităților suspecte și a coridorului {infra}",
            "objective_template": "Menținerea unei conștiințe persistente asupra {entities} și a coridorului {infra}.",
            "rationale_template": "Selectat deoarece situația necesită o observație mai bună înainte de a fi luate măsuri cu frecare mai mare."
        },
        "hu": {
            "title_template": "Növekedés az ISR Fedezettségben és Megfigyelésben",
            "description_template": "Ajánlott növelni az ISR fedezettséget, hogy fenntartva tartsa a {entities} tartós megfigyelését. Koordinálni kell a rendelkezésre álló taktikai UAV eszközökkel és a vệgi megfigyelési kérésekkel a {infra} korridor fedezettségének javítására.",
            "assumptions": [
                "Az ISR eszközöket 30 perc alatt átirányíthatják",
                "Az időjárás engedi a UAV működését a területen",
                "A vệgi visszajelzési idő elfogadható a nyomon követéshez"
            ],
            "expected_effect_template": "Gyanús entitások és {infra} korridor tartós megfigyelése",
            "objective_template": "{entities} és a {infra} korridor tartós tudatosságának fenntartása.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a helyzet jobb megfigyelést igényel, mielőtt magasabb frikciójú intézkedéseket fontolnának meg."
        },
        "bg": {
            "title_template": "Увеличаване на ISR Покритието и Наблюдението",
            "description_template": "Препоръчва се увеличаване на ISR покритието за поддържане на постоянна видимост на {entities}. Координирайте с наличните тактически UAV активи и заявки за сателитно наблюдение, за да подобрите покритието на коридора {infra}.",
            "assumptions": [
                "ISR активите могат да бъдат пренасочени в рамките на 30 минути",
                "Времето позволява UAV операции в района",
                "Времето за повторно сканиране на сателита е приемливо за проследяване"
            ],
            "expected_effect_template": "Постоянно наблюдение на подозрителни обекти и коридора {infra}",
            "objective_template": "Поддържане на постоянна осведоменост за {entities} и коридора {infra}.",
            "rationale_template": "Избрано, защото ситуацията изисква по-добро наблюдение, преди да бъдат обмислени мерки с по-висока фрикция."
        },
        "hr": {
            "title_template": "Povećanje Pokrivenosti i Nadzora ISR-a",
            "description_template": "Preporučuje se povećanje pokrivenosti ISR-a za održavanje stalnog nadzora {entities}. Koordinirati s dostupnim taktičkim UAV sredstvima i zahtjevima za satelitski nadzor kako bi se poboljšala pokrivenost koridora {infra}.",
            "assumptions": [
                "ISR sredstva mogu biti preusmjerena u roku od 30 minuta",
                "Vrijeme pogoduje operacijama UAV u tom području",
                "Vrijeme ponovnog snimanja satelita je prihvatljivo za praćenje"
            ],
            "expected_effect_template": "Stalni nadzor sumnjivih entiteta i koridora {infra}",
            "objective_template": "Održavanje stalne svijesti o {entities} i koridoru {infra}.",
            "rationale_template": "Odabrano jer situacija zahtijeva bolji nadzor prije razmatranja mjera s većim otporom."
        },
        "sk": {
            "title_template": "Zvýšiť pokrytie a sledovanie ISR",
            "description_template": "Odporúča sa zvýšiť pokrytie ISR na udržanie trvalého sledovania {entities}. Koordinovať s dostupnými taktickými UAV aktívami a požiadavkami na satelitné sledovanie na zlepšenie pokrytia koridoru {infra}.",
            "assumptions": [
                "ISR aktíva sa môžu presmerovať do 30 minút",
                "Počasie umožňuje operácie UAV v oblasti",
                "Čas opakovaného sledovania satelitom je akceptovateľný pre sledovanie"
            ],
            "expected_effect_template": "Trvalé sledovanie podozritých entit a koridoru {infra}",
            "objective_template": "Udržať trvalé povedomie o {entities} a koridore {infra}.",
            "rationale_template": "Vybrané, pretože situácia vyžaduje lepšie sledovanie pred zvážením meraní s vyšším odporom."
        },
        "sl": {
            "title_template": "Povečanje pokrivanja in opažanja ISR",
            "description_template": "Priporoča se povečanje pokrivanja ISR za vzdrževanje trajnostnega opažanja {entities}. Koordinirajte z dostopnimi taktičnimi UAV sredstvi in zahtevami za satelitsko opažanje za izboljšanje pokrivanja koridora {infra}.",
            "assumptions": [
                "ISR sredstva se lahko preusmerijo v roku 30 minut",
                "Vreme omogoča operacije UAV v območju",
                "Čas ponovnega obiska satelita je sprejemljiv za sledenje"
            ],
            "expected_effect_template": "Trajno opažanje podejneških entitetov in koridora {infra}",
            "objective_template": "Ohraniti trajnostno obvestitev o {entities} in koridoru {infra}.",
            "rationale_template": "Izbrano, ker situacija zahteva boljšo opažanje, preden se razmislijo o merjih z večjim odporom."
        },
        "et": {
            "title_template": "Täpsustada ISR katte ja jälgimine",
            "description_template": "Soovitatakse ISR katte suurendamist, et tagada pidev jälgimine {entities}. Koordineerage olemasolevate taktisete UAV varade ja satelliitjälgimise taotlustega {infra} koridori katte parandamiseks.",
            "assumptions": [
                "ISR varad saab ümber suunata 30 minuti jooksul",
                "Ilmastiku lubab UAV operatsioonid alalal",
                "Satelliitide uuesti külastamise aeg on jälgimise jaoks aktsepteeriv"
            ],
            "expected_effect_template": "Pidev jälgimine kahtluseelsete entiteedide ja {infra} koridori kohta",
            "objective_template": "Tagada pidev teadlikkus {entities} ja {infra} koridori kohta.",
            "rationale_template": "Valitud, sest olukord nõuab paremat jälgimist enne, kui kaalutatakse kõrgemad friktsiooni meetmed."
        },
        "lv": {
            "title_template": "Palielināt ISR Apkalpošanu un Uzskatīšanu",
            "description_template": "Ieteicams palielināt ISR apkalpošanu, lai saglabātu pastāvīgu uzskatīšanu par {entities}. Koordinēt ar pieejamajiem taktisko UAV resursiem un satelītu observācijas pieprasījumiem, lai uzlabotu {infra} koridora apkalpošanu.",
            "assumptions": [
                "ISR resursus var pārvirzīt 30 minūtu laikā",
                "Meteoroloģija atļauj UAV darbību šajā teritorijā",
                "Satelītu atkārtotas apmeklēšanas laiks ir pieņemams izsekot"
            ],
            "expected_effect_template": "Pastāvīga uzskatīšana par aizdomīgiem entitātēm un {infra} koridora",
            "objective_template": "Saglabāt pastāvīgu zināšanu par {entities} un {infra} koridora.",
            "rationale_template": "Izvēlēts, jo situācija prasa labāku observāciju pirms tiek apskatītas augstāk slodzamās pasākumus."
        },
        "lt": {
            "title_template": "Padidinti ISR Pokrovimą ir Beobavavimą",
            "description_template": "Regaliam padidinti ISR pokrovimą, kad išlaikytų nuolatinį stebėjimą {entities}. Koordinuoti su prieinamais taktiniais UAV ištekliais ir dirbtinio satelito stebėjimo prašymais, kad pagerintų {infra} koridoro pokrovimą.",
            "assumptions": [
                "ISR ištekliai gali būti nukreipti per 30 minučių",
                "Oras leidžia UAV veikimą šioje sriti",
                "Satelito pasikartojimo laikas yra priimtinas sekti"
            ],
            "expected_effect_template": "Nuolatinis stebėjimas įtarimų padėgtių entidades ir {infra} koridoro",
            "objective_template": "Išlaikyti nuolatinį supratimą apie {entities} ir {infra} koridorą.",
            "rationale_template": "Pasirinkta, nes situacija reikalauja geresnio stebėjimo prieš apsvaraujant aukštesnius tarpojius priemones."
        },
        "da": {
            "title_template": "Øg ISR Dækning og Observation",
            "description_template": "Anbefaler øget ISR dækning for at opretholde vedvarende observation af {entities}. Koordiner med tilgængelige taktiske UAV-aktiver og satellitobservationsanmodninger for at forbedre dækningen af {infra} korridoren.",
            "assumptions": [
                "ISR aktiver kan omdirigeres inden for 30 minutter",
                "Vejret tillader UAV-operationer i området",
                "Satellitgenbesøgstid er acceptabel for sporing"
            ],
            "expected_effect_template": "Vedvarende observation af mistænkelige enheder og {infra} korridoren",
            "objective_template": "Oprethold vedvarende bevidsthed over {entities} og {infra} korridoren.",
            "rationale_template": "Valgt, fordi situationen kræver bedre observation, før højere friktionsmæssige foranstaltninger overvejes."
        },
        "no": {
            "title_template": "Øke ISR-dekning og observasjon",
            "description_template": "Anbefaler å øke ISR-dekningen for å opprettholde vedvarende observasjon av {entities}. Koordinere med tilgjengelige taktiske UAV-ressurser og satellittobservasjonsforespørsler for å forbedre dekningen av {infra}-korridoren.",
            "assumptions": [
                "ISR-ressurser kan omdirigeres innen 30 minutter",
                "Været tillater UAV-operasjoner i området",
                "Satellittgjenopptakstid er akseptabel for sporing"
            ],
            "expected_effect_template": "Vedvarende observasjon av mistenkelige enheter og {infra}-korridoren",
            "objective_template": "Opprettholde vedvarende bevissthet over {entities} og {infra}-korridoren.",
            "rationale_template": "Valgt fordi situasjonen krever bedre observasjon før høyere friksjonsmål vurderes."
        },
        "is": {
            "title_template": "Auka ISR-þekking og eftirlit",
            "description_template": "Mætir með að auka ISR-þekkinguna til að viðhalda stöðugum eftirliti yfir {entities}. Samræmd með til staðandi taktískum UAV-auðlindum og beiðum um satellit eftirlit til að bæta þekkinguna á {infra} gangbrautinni.",
            "assumptions": [
                "ISR auðlindir geta verið endirbeint innan 30 mínútum",
                "Vatn veitir UAV-virkni í svæðinu",
                "Satellit endurferðartími er viðkvæmur fyrir eftirlit"
            ],
            "expected_effect_template": "Stöðugt eftirlit yfir mistökum viðkvæmum aðilum og {infra} gangbrautinni",
            "objective_template": "Viðhalda stöðugri varkárni yfir {entities} og {infra} gangbrautinni.",
            "rationale_template": "Valinn því að tilgangslefin þarf betri eftirlit áður en meiri álagandi aðgerðir eru skoðaðar."
        },
        "fi": {
            "title_template": "Lisää ISR-kattoa ja havainnointia",
            "description_template": "Suositellaan ISR-katon lisäämistä jatkuvan havainnoinnin ylläpitämiseksi {entities}:n kohdalla. Koordinoi saatavilla olevien taktisien UAV-toimintojen ja satelliittihavainto-pyyntöjen kanssa kattavuuden parantamiseksi {infra}-koridorin alueella.",
            "assumptions": [
                "ISR-varusteet voidaan ohjata uudelleen 30 minuutissa",
                "Sää mahdollistaa UAV-toiminnan alueella",
                "Satelliittien uudelleenkäyntiaika on hyväksyttävä seurantaan"
            ],
            "expected_effect_template": "Jatkuva havainnointi epäilyttävistä kohteista ja {infra}-koridorista",
            "objective_template": "Ylläpidä jatkuvaa tietoisuutta {entities}:n ja {infra}-koridorin alueella.",
            "rationale_template": "Valittu, koska tilanne vaatii parempaa havainnointia ennen korkeamman kitkan toimenpiteiden harkitsemista."
        },
        "sv": {
            "title_template": "Öka ISR-täckningen och observationen",
            "description_template": "Rekommenderar att öka ISR-täckningen för att bibehålla kontinuerlig observation av {entities}. Koordinera med tillgängliga taktiska UAV-tillgångar och satellitobservationsförfrågningar för att förbättra täckningen av {infra}-korridoren.",
            "assumptions": [
                "ISR-tillgångar kan omdirigeras inom 30 minuter",
                "Vädret tillåter UAV-operationer i området",
                "Satellitåterbesökstid är acceptabel för spårning"
            ],
            "expected_effect_template": "Kontinuerlig observation av misstänkta enheter och {infra}-korridoren",
            "objective_template": "Bibehålla kontinuerlig medvetenhet över {entities} och {infra}-korridoren.",
            "rationale_template": "Vald eftersom situationen kräver bättre observation innan högre friktionsåtgärder övervägs."
        },
        "sq": {
            "title_template": "Rritniqja e Krijimit të ISR dhe Vëzhgimit",
            "description_template": "Rekomandojmë rritjen e mbulimit ISR për të mbajtur vëzhgim të vazhdueshëm të {entities}. Koordinoni me asetet e UAV taktike të disponueshme dhe kërkesat e vëzhgimit satelitar për të përmirësuar mbulimin e korridorit {infra}.",
            "assumptions": [
                "Asetet ISR mund të riorientohen brenda 30 minutash",
                "Klima lejon operacionet e UAV në zonë",
                "Koha e rivizitimit satelitar është e pranueshme për gjurmimin"
            ],
            "expected_effect_template": "Vëzhgim i vazhdueshëm i entiteteve të dyshuara dhe korridorit {infra}",
            "objective_template": "Mbani ndërgjegjësim të vazhdueshëm mbi {entities} dhe korridorin {infra}.",
            "rationale_template": "Zgjedhur sepse situata kërkon vëzhgim më të mirë para se të konsiderohen masat me fërkim më të lartë."
        },
        "mk": {
            "title_template": "Зголемување на покриењето и следењето на ISR",
            "description_template": "Препорачуваме зголемување на ISR покриењето за одржување континуирано следење на {entities}. Координирајте со достапните тактички UAV активи и барања за сателитско следење за подобрување на покриењето на коридорот {infra}.",
            "assumptions": [
                "ISR активите можат да бидат пренасочени во рок од 30 минути",
                "Времето овозможува UAV операции во областа",
                "Времето на повторно посетување на сателитот е прифатливо за следење"
            ],
            "expected_effect_template": "Континуирано следење на сомнежните ентитети и коридорот {infra}",
            "objective_template": "Одржување континуирана свесност за {entities} и коридорот {infra}.",
            "rationale_template": "Избрано бидејќи ситуацијата бара подобар надзор пред да се разгледаат мерки со поготка friction."
        },
        "me": {
            "title_template": "Povećanje Pokrivenosti i Nadzora ISR",
            "description_template": "Preporučuje se povećanje ISR pokrivenosti radi održavanja stalnog nadzora {entities}. Koordinirati sa dostupnim taktičkim UAV sredstvima i zahtevima za satelitski nadzor radi poboljšanja pokrivenosti koridora {infra}.",
            "assumptions": [
                "ISR sredstva mogu biti preusmerena u roku od 30 minuta",
                "Vreme dozvoljava operacije UAV u tom području",
                "Vreme ponovnog snimanja satelita je prihvatljivo za praćenje"
            ],
            "expected_effect_template": "Stalni nadzor sumnjivih entiteta i koridora {infra}",
            "objective_template": "Održavanje stalne svesti o {entities} i koridoru {infra}.",
            "rationale_template": "Odabrano jer situacija zahteva bolji nadzor pre nego što se razmotre mere sa većim otporom."
        },
        "el": {
            "title_template": "Αύξηση της Επα coverage και Παρατήρησης",
            "description_template": "Συνιστάται η αύξηση της κάλυψης ISR για τη διατήρηση συνεχούς παρατήρησης των {entities}. Συντονισμός με τα διαθέσιμα τακτικά UAV περιουσιακά στοιχεία και αιτήματα παρατήρησης από δορυφόρους για βελτίωση της κάλυψης του διαδρόμου {infra}.",
            "assumptions": [
                "Τα περιουσιακά στοιχεία ISR μπορούν να ανακατευθυνθούν εντός 30 λεπτών",
                "Ο καιρός επιτρέπει τις επιχειρήσεις UAV στην περιοχή",
                "Ο χρόνος επανεξέτασης του δορυφόρου είναι αποδεκτός για παρακολούθηση"
            ],
            "expected_effect_template": "Συνεχής παρατήρηση ύποπτων οντοτήτων και του διαδρόμου {infra}",
            "objective_template": "Διατήρηση συνεχούς ενημέρωσης για τα {entities} και τον διάδρομο {infra}.",
            "rationale_template": "Επιλέχθηκε επειδή η κατάσταση απαιτεί καλύτερη παρατήρηση πριν εξεταστούν μέτρα υψηλότερης τριβής."
        }
    },
    "COA-TPL-SHADOW": {
        "en": {
            "title_template": "Shadow Suspicious Vessels with Allied Maritime Assets",
            "description_template": "Recommend allied maritime patrol assets maintain visual and radar contact with {entities}. Maintain safe distance. Document activity and report observations through established channels.",
            "assumptions": [
                "Allied naval assets are available within 60 minutes",
                "Rules of observation are clearly communicated",
                "Vessels will not attempt evasion at high speed"
            ],
            "expected_effect_template": "Direct observation and deterrence through presence near {entities}",
            "objective_template": "Maintain close observation of {entities} using allied maritime presence.",
            "rationale_template": "Selected because the threat picture suggests continued contact management and pattern collection are required."
        },
        "es": {
            "title_template": "Hacer sombra a buques sospechosos con medios marítimos aliados",
            "description_template": "Se recomienda que medios de patrulla marítima aliados mantengan contacto visual y radar con {entities}. Mantener distancia de seguridad. Documentar la actividad e informar las observaciones por los canales establecidos.",
            "assumptions": [
                "Hay medios navales aliados disponibles en 60 minutos",
                "Las reglas de observación están claramente comunicadas",
                "Los buques no intentarán evasión a alta velocidad"
            ],
            "expected_effect_template": "Observación directa y disuasión mediante presencia cerca de {entities}",
            "objective_template": "Mantener observación cercana de {entities} mediante presencia marítima aliada.",
            "rationale_template": "Se selecciona porque la imagen de amenaza sugiere que se requiere gestión continuada del contacto y recopilación de patrones."
        },
        "fr": {
            "title_template": "Suivre les Navires Suspects avec les Actifs Maritimes Alliés",
            "description_template": "Recommander aux actifs de patrouille maritime alliés de maintenir un contact visuel et radar avec les {entities}. Maintenir une distance de sécurité. Documenter l'activité et signaler les observations par les canaux établis.",
            "assumptions": [
                "Les actifs navals alliés sont disponibles dans les 60 minutes",
                "Les règles d'observation sont clairement communiquées",
                "Les navires n'essaieront pas d'éviter à grande vitesse"
            ],
            "expected_effect_template": "Observation directe et dissuasion par la présence près des {entities}",
            "objective_template": "Maintenir une observation rapprochée des {entities} en utilisant la présence maritime alliée.",
            "rationale_template": "Sélectionné car le tableau de la menace suggère que la gestion continue des contacts et la collecte de schémas sont nécessaires."
        },
        "de": {
            "title_template": "Verdächtige Schiffe mit alliierten maritimen Assets beobachten",
            "description_template": "Empfiehlt, dass alliierte maritime Patrouillen-Assets visuellen und Radar-Kontakt mit {entities} aufrechterhalten. Halten Sie einen sicheren Abstand. Dokumentieren Sie die Aktivitäten und melden Sie Beobachtungen über etablierte Kanäle.",
            "assumptions": [
                "Alliierte Marineassets sind innerhalb von 60 Minuten verfügbar",
                "Die Beobachtungsregeln sind klar kommuniziert",
                "Die Schiffe werden nicht versuchen, mit hoher Geschwindigkeit auszuweichen"
            ],
            "expected_effect_template": "Direkte Beobachtung und Abschreckung durch Präsenz in der Nähe von {entities}",
            "objective_template": "Aufrechterhaltung der engen Beobachtung von {entities} unter Nutzung der alliierten maritimen Präsenz.",
            "rationale_template": "Ausgewählt, da das Bedrohungsbild eine fortgesetzte Kontaktverwaltung und Mustererfassung erfordert."
        },
        "it": {
            "title_template": "Sorvegliare le Navi Sospette con Asset Marittimi Alleati",
            "description_template": "Si raccomanda agli asset di pattugliamento marittimo alleati di mantenere il contatto visivo e radar con {entities}. Mantenere una distanza di sicurezza. Documentare l'attività e segnalare le osservazioni attraverso i canali stabiliti.",
            "assumptions": [
                "Gli asset navali alleati sono disponibili entro 60 minuti",
                "Le regole di osservazione sono chiaramente comunicate",
                "Le navi non tenteranno di sfuggire ad alta velocità"
            ],
            "expected_effect_template": "Osservazione diretta e deterrenza attraverso la presenza vicino a {entities}",
            "objective_template": "Mantenere un'osservazione ravvicinata di {entities} utilizzando la presenza marittima alleata.",
            "rationale_template": "Selezionato perché il quadro della minaccia suggerisce che sono necessari un continuo management del contatto e la raccolta di pattern."
        },
        "pt": {
            "title_template": "Acompanhar Embarcações Suspeitas com Ativos Marítimos Aliados",
            "description_template": "Recomenda-se que os ativos de patrulha marítima aliados mantenham contato visual e de radar com {entities}. Manter distância segura. Documentar a atividade e relatar observações através dos canais estabelecidos.",
            "assumptions": [
                "Ativos navais aliados estão disponíveis em 60 minutos",
                "As regras de observação são claramente comunicadas",
                "As embarcações não tentarão evasão em alta velocidade"
            ],
            "expected_effect_template": "Observação direta e dissuasão através da presença perto de {entities}",
            "objective_template": "Manter observação próxima de {entities} usando a presença marítima aliada.",
            "rationale_template": "Selecionado porque o quadro de ameaças sugere que a gestão contínua de contato e a coleta de padrões são necessárias."
        },
        "nl": {
            "title_template": "Schaduw Verdachte Schepen met Geallieerde Maritieme Middelen",
            "description_template": "Aanbeveling dat geallieerde maritieme patrouillemiddelen visueel en radarcontact behouden met {entities}. Houd een veilige afstand. Documenteer activiteiten en rapporteer observaties via gevestigde kanalen.",
            "assumptions": [
                "Geallieerde marine middelen zijn binnen 60 minuten beschikbaar",
                "Observatieregels zijn duidelijk gecommuniceerd",
                "Schepen zullen niet proberen te ontwijken met hoge snelheid"
            ],
            "expected_effect_template": "Directe observatie en afschrikking door aanwezigheid nabij {entities}",
            "objective_template": "Handhaven van nauwkeurige observatie van {entities} met behulp van geallieerde maritieme aanwezigheid.",
            "rationale_template": "Gekozen omdat het dreigingsbeeld suggereert dat voortdurende contactbeheer en patroonverzameling vereist zijn."
        },
        "pl": {
            "title_template": "Śledzenie Podejrzanych Okrętów za Pomocą Sojuszniczych Zasobów Morskich",
            "description_template": "Rekomenduje się, aby sojusznicze zasoby patrolowe morskie utrzymywały kontakt wizualny i radarowy z {entities}. Utrzymywać bezpieczną odległość. Dokumentować aktywność i zgłaszać obserwacje przez ustalone kanały.",
            "assumptions": [
                "Sojusznicze zasoby marynarki wojennej są dostępne w ciągu 60 minut",
                "Zasady obserwacji są jasno zakomunikowane",
                "Okręty nie będą próbowały uciec z dużą prędkością"
            ],
            "expected_effect_template": "Bezpośrednia obserwacja i odstraszanie poprzez obecność w pobliżu {entities}",
            "objective_template": "Utrzymanie bliskiej obserwacji {entities} przy użyciu sojuszniczej obecności morskiej.",
            "rationale_template": "Wybrano, ponieważ obraz zagrożenia sugeruje konieczność kontynuowania zarządzania kontaktem i zbierania wzorców."
        },
        "tr": {
            "title_template": "Müttefik Deniz Varlıklarıyla Şüpheli Gemileri Gölgeleme",
            "description_template": "Müttefik deniz devriye varlıklarının {entities} ile görsel ve radar temasını sürdürmesini tavsiye eder. Güvenli mesafeyi koruyun. Faaliyeti belgeleyin ve gözlemleri yerleşik kanallar aracılığıyla raporlayın.",
            "assumptions": [
                "Müttefik deniz varlıkları 60 dakika içinde mevcut",
                "Gözlem kuralları açıkça iletilmiştir",
                "Gemiler yüksek hızda kaçma girişiminde bulunmayacaktır"
            ],
            "expected_effect_template": "{entities} yakınında varlık yoluyla doğrudan gözlem ve caydırıcılık",
            "objective_template": "Müttefik deniz varlığı kullanarak {entities}'nın yakın takibini sürdürmek.",
            "rationale_template": "Seçildi çünkü tehdit resmi, sürekli temas yönetimi ve desen toplamanın gerekli olduğunu göstermektedir."
        },
        "cs": {
            "title_template": "Sledovat podezřelé lodě spojeneckými maritimními prostředky",
            "description_template": "Doporučuje se spojeneckým maritimním patrolovacím prostředkům udržovat vizuální a radarový kontakt s {entities}. Udržovat bezpečnou vzdálenost. Dokumentovat činnost a hlášit pozorování prostřednictvím zavedených kanálů.",
            "assumptions": [
                "Spojenecké námořní prostředky jsou dostupné do 60 minut",
                "Pravidla pozorování jsou jasně komunikována",
                "Lodě se nebudou snažit uniknout s vysokou rychlostí"
            ],
            "expected_effect_template": "Přímé pozorování a odrazování prostřednictvím přítomnosti poblíž {entities}",
            "objective_template": "Udržet těsné pozorování {entities} pomocí spojenecké maritimní přítomnosti.",
            "rationale_template": "Vybráno, protože obraz hrozby naznačuje, že je nutné pokračovat v řízení kontaktu a sběru vzorců."
        },
        "ro": {
            "title_template": "Umbrarea Navelor Suspecte cu Active Maritime Aliate",
            "description_template": "Se recomandă ca resursele de patrulare maritimă aliate să mențină contact vizual și radar cu {entities}. Mențineți o distanță sigură. Documentați activitatea și raportați observațiile prin canalele stabilite.",
            "assumptions": [
                "Activele navale aliate sunt disponibile în decurs de 60 de minute",
                "Regulile de observație sunt comunicate clar",
                "Navele nu vor încerca să evadeze la viteză mare"
            ],
            "expected_effect_template": "Observare directă și deterență prin prezența în apropierea {entities}",
            "objective_template": "Menținerea unei observații apropiate asupra {entities} folosind prezența maritimă aliată.",
            "rationale_template": "Selectat deoarece imaginea amenințării sugerează că este necesară gestionarea continuă a contactului și colectarea de modele."
        },
        "hu": {
            "title_template": "Árnyékolni a Gyanús Térvízi Eseteket Szövetséges Tengeri Eszközökkel",
            "description_template": "Ajánlott a szövetséges tengeri őrző eszközöknek fenntartani vizuális és radarski kapcsolatot a {entities} vel. Tartani biztonságos távolságot. Dokumentálni a tevékenységet és jelenteni a megfigyeléseket a kialakított csatornákon keresztül.",
            "assumptions": [
                "A szövetséges tengeri eszközök 60 perc alatt elérhetők",
                "A megfigyelési szabályok világosan kommunikáltak",
                "A csónakok nem fognak megpróbálni elkerülni magas sebességgel"
            ],
            "expected_effect_template": "Direkt megfigyelés és elriasztás a {entities} közelében való jelenlét által",
            "objective_template": "A szövetséges tengeri jelenlét használatával közel megfigyelni a {entities}-t.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a fenyegetési kép jelzi, hogy folytatott kapcsolatkezelés és mintaművek gyűjtése szükséges."
        },
        "bg": {
            "title_template": "Следване на Подозрени Кораби с Съюзни Морски Активи",
            "description_template": "Препоръчва се съюзните морски патрулни активи да поддържат визуално и радиолокационно съприкосновение с {entities}. Поддържайте безопасна дистанция. Документирайте дейността и докладвайте наблюденията през установените канали.",
            "assumptions": [
                "Съюзните морски активи са налични в рамките на 60 минути",
                "Правилата за наблюдение са ясно комуникирани",
                "Корабите няма да се опитат да избягат с висока скорост"
            ],
            "expected_effect_template": "Директно наблюдение и сдържане чрез присъствие близо до {entities}",
            "objective_template": "Поддържане на близко наблюдение на {entities} с помощта на съюзно морско присъствие.",
            "rationale_template": "Избрано, защото картината на заплаха предполага, че е необходим продължителен контрол на контакта и събиране на модели."
        },
        "hr": {
            "title_template": "Praćenje Sumnjivih Brodova Slijedimo Saveznim Pomorskim Sredstvima",
            "description_template": "Preporučuje se saveznim pomorskim patrulnim sredstvima da održavaju vizualni i radarski kontakt s {entities}. Održavati sigurnu udaljenost. Dokumentirati aktivnosti i izvještavati o zapažanjima putem uspostavljenih kanala.",
            "assumptions": [
                "Savezni pomorski sredstva su dostupna u roku od 60 minuta",
                "Pravila nadzora su jasno komunicirana",
                "Brodovi neće pokušati izbjegavanje na visokoj brzini"
            ],
            "expected_effect_template": "Direktan nadzor i odvraćanje kroz prisutnost u blizini {entities}",
            "objective_template": "Održavanje bliskog nadzora {entities} koristeći savezni pomorski prisutnost.",
            "rationale_template": "Odabrano jer slika prijetnje sugerira da je potrebno nastaviti s upravljanjem kontaktima i prikupljanjem obrazaca."
        },
        "sk": {
            "title_template": "Sledovať podozrité súbošť s pomocou spojeneckých morských aktív",
            "description_template": "Odporúča sa spojeneckým morským patrolovacím aktívam udržiavať vizuálny a radarový kontakt s {entities}. Udržiavať bezpečnú vzdialenosť. Dokumentovať činnosť a hlásiť pozorovanie prostredníctvom ustanovených kanálov.",
            "assumptions": [
                "Spojenecké námorné aktíva sú dostupné do 60 minút",
                "Pravidlá sledovania sú jasne komunikované",
                "Súbošť sa nespokúsi vyhýbať pri vysokej rýchlosti"
            ],
            "expected_effect_template": "Priame sledovanie a odstrašovanie prostredníctvom prítomnosti blízko {entities}",
            "objective_template": "Udržať blízke sledovanie {entities} pomocou spojeneckej morsk ej prítomnosti.",
            "rationale_template": "Vybrané, pretože obraz hrozby naznačuje, že je potrebné pokračovať v riadení kontaktu a zhromažďovaní vzorcov."
        },
        "sl": {
            "title_template": "Sledenje podejneškim čolunom z zavezniškimi pomorskimi sredstvi",
            "description_template": "Priporoča se zavezniškim pomorskim patrulnim sredstvam vzdrževanje vizualnega in radarskega kontakta z {entities}. Ohraniti varno daljavo. Dokumentirati dejavnosti in poročati opažanja skozi ustvarjene kanale.",
            "assumptions": [
                "Zavezniška pomorska sredstva so na voljo v roku 60 minut",
                "Pravila opažanja so jasno sporočena",
                "Čoluni ne bodo poskušali izogniti se z visoko hitrostjo"
            ],
            "expected_effect_template": "Direktno opažanje in odvraščanje z uporabo prisotnosti blizu {entities}",
            "objective_template": "Ohraniti bližnje opažanje {entities} z uporabo zavezniške pomorske prisotnosti.",
            "rationale_template": "Izbrano, ker slika amebe kaže, da je potrebno nadaljnje upravljanje kontakta in zbiranje vzorcev."
        },
        "et": {
            "title_template": "Varjenda kahtluseelseteid laevadeid liitaste mereliste varadega",
            "description_template": "Soovitatakse liitaste mereliste patrollivarade jälgida visuaalset ja radaarkontakti {entities} kanssa. Püsige turvalises kauguses. Dokumenteerige tegevus ja raporteerige jälgimised käesolevate kanalite kaudu.",
            "assumptions": [
                "Liitaste merelised varad on saadaval 60 minuti jooksul",
                "Jälgimise reeglid on selgelt kommunikeeritud",
                "Laevad ei ürita kõrvalduda kõrge nopeusega"
            ],
            "expected_effect_template": "Direkts jälgimine ja hävitamine lähenemise kaudu {entities} läheduses",
            "objective_template": "Tagada lähedane jälgimine {entities} liitaste merelise lähenduse abil.",
            "rationale_template": "Valitud, sest ohtlik pilt nõuab pidevat kontakti haldamist ja sümmetriate kogumist."
        },
        "lv": {
            "title_template": "Atsekt aizdomīgas kuģus ar alliēšu jūras resursiem",
            "description_template": "Ieteicams alliēšu jūras patrulhas resursiem saglabāt vizuālu un radara kontaktu ar {entities}. Saglabāt drošu attālumu. Dokumentēt aktivitāti un ziņot observācijas caur veiktajiem kanāliem.",
            "assumptions": [
                "Alliēšu navais resursi ir pieejami 60 minūtu laikā",
                "Observācijas noteikumi ir skaidri paziņoti",
                "Kuģi neatcerēsies ar augstas ātruma ievadīšanu"
            ],
            "expected_effect_template": "Tiešā observācija un atgriezeniskums klātbūtnes caur {entities} tuvumā",
            "objective_template": "Saglabāt tuvu observāciju par {entities} izmantojot alliēšu jūras klātbūtni.",
            "rationale_template": "Izvēlēts, jo draudens attēls norāda, ka ir nepieciešams turpināt kontakta vadību un modeļu savākšanu."
        },
        "lt": {
            "title_template": "Sekti Įtarimų Laivus Alysių Jūrinių Išteklių Pagal",
            "description_template": "Regaliam alysių jūrinių patrolybos ištekliams išlaikyti vizualų ir radaro kontaktą su {entities}. Išlaikyti saugią atstumą. Dokumentuoti veikimą ir pranešti apie pastebėjimus per nustatytus kanalus.",
            "assumptions": [
                "Alysių jūrinių išteklių yra prieinami per 60 minučių",
                "Stebėjimo taisyklės aiškiai pranešiamas",
                "Laivai nebandys išvykti greituje tempu"
            ],
            "expected_effect_template": "Direkti stebėjimas ir išgaičymas esant prie {entities}",
            "objective_template": "Išlaikyti kampinią stebėjimą {entities} naudojant alysių jūrinį buvimą.",
            "rationale_template": "Pasirinkta, nes grėsmės vaizdas rodo, kad reikia tęsti kontakto valdymą ir modelių rinkimą."
        },
        "da": {
            "title_template": "Skygge Mistænkelige Fartøjer med Allierede Maritime Aktiver",
            "description_template": "Anbefaler, at allierede maritime patruljeaktiver opretholder visuel og radar kontakt med {entities}. Oprethold sikker afstand. Dokumenter aktivitet og rapporter observationer gennem etablerede kanaler.",
            "assumptions": [
                "Allierede flådeaktiver er tilgængelige inden for 60 minutter",
                "Observationsregler er klart kommunikeret",
                "Fartøjer vil ikke forsøge at undvige med høj hastighed"
            ],
            "expected_effect_template": "Direkte observation og afskrækkelse gennem tilstedeværelse nær {entities}",
            "objective_template": "Oprethold tæt observation af {entities} ved hjælp af allieret maritim tilstedeværelse.",
            "rationale_template": "Valgt, fordi trusselsbilledet indikerer, at fortsat kontaktstyring og mønsterindsamling er nødvendig."
        },
        "no": {
            "title_template": "Skygge mistenkelige fartøyer med allierte maritime ressurser",
            "description_template": "Anbefaler at allierte maritime patruljeaktiva opprettholder visuell og radar kontakt med {entities}. Opprettholde trygg avstand. Dokumentere aktivitet og rapportere observasjoner gjennom etablerte kanaler.",
            "assumptions": [
                "Allierte marineaktiva er tilgjengelige innen 60 minutter",
                "Observasjonsregler er tydelig kommunisert",
                "Fartøyene vil ikke forsøke å unngå på høy hastighet"
            ],
            "expected_effect_template": "Direkte observasjon og avskrekking gjennom tilstedeværelse nær {entities}",
            "objective_template": "Opprettholde nær observasjon av {entities} ved bruk av alliert maritim tilstedeværelse.",
            "rationale_template": "Valgt fordi trusselbildet indikerer at fortsatt kontaktstyring og mønsterinnsamling er nødvendig."
        },
        "is": {
            "title_template": "Skugga mistökum skipum með samstarfandi sjóauðlindum",
            "description_template": "Mætir með að samstarfandi sjóauðlindir halda mynd- og radarsambandi við {entities}. Halda öruggum fjarlægð. Skrá setja virkni og skila eftirlit áfram í samþættum leiðum.",
            "assumptions": [
                "Samstarfandi sjóauðlindir eru til staðar innan 60 mínútum",
                "Reglur eftirlits eru skýrt samskiptaðar",
                "Skipin mun ekki reyna á að sleppa í háu hraða"
            ],
            "expected_effect_template": "Bein eftirlit og óskilja í gegnum tilvist nær {entities}",
            "objective_template": "Halda nálægt eftirliti yfir {entities} með samstarfandi sjólegri tilvist.",
            "rationale_template": "Valinn því að hættulegs mynd er að gefa til kynna að stöðugt sambandsstjórnun og samlanir mönnuðra mönnu eru nauðsynlegar."
        },
        "fi": {
            "title_template": "Seuraa epäilyttäviä aluksia liittoutuneiden merivoimien avulla",
            "description_template": "Suositellaan liittoutuneiden merivalvontavarusteiden ylläpitävän visuaalista ja radariautomaattista kontaktia {entities}:n kanssa. Pidä turvallinen etäisyys. Dokumentoi toiminta ja raportoi havainnot vakiintuneiden kanavien kautta.",
            "assumptions": [
                "Liittoutuneet laivavarusteet ovat saatavilla 60 minuutissa",
                "Havainnointisäännöt on kommunikoitu selkeästi",
                "Alukset eivät yritä paeta suurilla nopeuksilla"
            ],
            "expected_effect_template": "Suora havainnointi ja pelote läsnäololla {entities}:n lähellä",
            "objective_template": "Ylläpidä läheistä havainnointia {entities}:n avulla liittoutuneen meripresenssin kautta.",
            "rationale_template": "Valittu, koska uhkakuvio viittaa siihen, että jatkuva kontaktin hallinta ja kuvioiden keruu ovat tarpeen."
        },
        "sv": {
            "title_template": "Skugga misstänkta fartyg med allierade sjötillgångar",
            "description_template": "Rekommenderar att allierade patrulltillgångar bibehåller visuell och radarkontakt med {entities}. Bibehåll säkert avstånd. Dokumentera aktivitet och rapportera observationer via etablerade kanaler.",
            "assumptions": [
                "Allierade sjötillgångar är tillgängliga inom 60 minuter",
                "Observationsregler kommuniceras tydligt",
                "Fartygen kommer inte att försöka undvika i hög hastighet"
            ],
            "expected_effect_template": "Direkt observation och avskräckning genom närvaro nära {entities}",
            "objective_template": "Bibehålla nära observation av {entities} med hjälp av allierad sjö närvaro.",
            "rationale_template": "Vald eftersom hotbilden tyder på att fortsatt kontakthantering och mönsterinsamling är nödvändigt."
        },
        "sq": {
            "title_template": "Hajroni Anije të Dyshuara me Asetet Detare të Aleatëve",
            "description_template": "Rekomandojmë asetet e patrullimit detar të aleatëve të mbajnë kontakt vizual dhe radari me {entities}. Mbani distancë të sigurt. Dokumentoni aktivitetin dhe raportoni vëzhgimet përmes kanaleve të vendosura.",
            "assumptions": [
                "Asetet ushtarake detare të aleatëve janë të disponueshme brenda 60 minutash",
                "Rregullat e vëzhgimit janë komunikuar qartë",
                "Anijet nuk do të përpiqen të shmangin në shpejtësi të lartë"
            ],
            "expected_effect_template": "Vëzhgim direkt dhe detirancë përmes pranisë pranë {entities}",
            "objective_template": "Mbani vëzhgim të ngushtë të {entities} duke përdorur praninë detare të aleatëve.",
            "rationale_template": "Zgjedhur sepse panorama e kërcënimit sugjeron se kërkohet menaxhim i vazhdueshëm i kontaktit dhe mbledhje e modeleve."
        },
        "mk": {
            "title_template": "Следење на сомнежните сакурници со сојузни морски активи",
            "description_template": "Препорачуваме сојузни морски патрулни активи да одржуваат визуелен и радарски контакт со {entities}. Одржувајте безбедна дистанца. Документирајте ја активност и известувајте ги наблюденията преку утврдени канали.",
            "assumptions": [
                "Сојузните морски активи се достапни во рок од 60 минути",
                "Правилата за следење се јасно комуницирани",
                "Сакурниците нема да се обидат да избегаат со висока брзина"
            ],
            "expected_effect_template": "Директно следење и одвраќање преку присуство покрај {entities}",
            "objective_template": "Одржување близок надзор на {entities} користејќи сојузно морско присуство.",
            "rationale_template": "Избрано бидејќи сликата на заканата сугерира дека се потребни продолжено управување со контактот и собирање на обрасци."
        },
        "me": {
            "title_template": "Praćenje Sumnjivih Brodova sa Saveznim Morskim Sredstvima",
            "description_template": "Preporučuje se saveznim morskim patrolnim sredstvima da održavaju vizuelni i radarski kontakt sa {entities}. Održavati bezbednu udaljenost. Dokumentovati aktivnosti i izveštavati o zapažanjima putem uspostavljenih kanala.",
            "assumptions": [
                "Savezni pomorski resursi su dostupni u roku od 60 minuta",
                "Pravila nadzora su jasno komunicirana",
                "Brodovi neće pokušati izbegavanje na visokoj brzini"
            ],
            "expected_effect_template": "Direktan nadzor i odvraćanje kroz prisustvo u blizini {entities}",
            "objective_template": "Održavanje bliskog nadzora {entities} korišćenjem saveznog morskog prisustva.",
            "rationale_template": "Odabrano jer slika pretnje ukazuje na potrebu za nastavkom upravljanja kontaktom i prikupljanja obrazaca."
        },
        "el": {
            "title_template": "Σκίαση Ύποπτων Πλοίων με Συμμαχικά Θαλάσσια Περιουσιακά Στοιχεία",
            "description_template": "Συνιστάται στα συμμαχικά θαλάσσια περιπολικά περιουσιακά στοιχεία να διατηρούν οπτική και ραντάρ επαφή με τα {entities}. Διατήρηση ασφαλούς απόστασης. Καταγραφή δραστηριότητας και αναφορά παρατηρήσεων μέσω των καθιερωμένων καναλιών.",
            "assumptions": [
                "Τα συμμαχικά ναυτικά περιουσιακά στοιχεία είναι διαθέσιμα εντός 60 λεπτών",
                "Οι κανόνες παρατήρησης επικοινωνούνται σαφώς",
                "Τα πλοία δεν θα προσπαθήσουν να αποφύγουν με υψηλή ταχύτητα"
            ],
            "expected_effect_template": "Άμεση παρατήρηση και αποτροπή μέσω παρουσίας κοντά στα {entities}",
            "objective_template": "Διατήρηση στενής παρατήρησης των {entities} χρησιμοποιώντας τη συμμαχική θαλάσσια παρουσία.",
            "rationale_template": "Επιλέχθηκε επειδή το εικόνα της απειλής υποδηλώνει ότι απαιτείται συνεχής διαχείριση επαφής και συλλογή μοτίβων."
        }
    },
    "COA-TPL-CABLE-PROTECT": {
        "en": {
            "title_template": "Prioritize Protection of {infra}",
            "description_template": "Given confirmed cable compromise, recommend prioritizing monitoring and protection of remaining {infra}. Consider assigning the nearest available allied maritime asset to observe the cable corridor. Coordinate with cable operator for continuous integrity monitoring.",
            "assumptions": [
                "Secondary infrastructure has not yet been compromised",
                "Nearest allied asset can reach the area within 90 minutes",
                "Cable operator can provide continuous integrity status"
            ],
            "expected_effect_template": "Reduced risk of further compromise to {infra}",
            "objective_template": "Protect remaining {infra} from follow-on disruption.",
            "rationale_template": "Selected because confirmed infrastructure compromise shifts priority toward protecting the remaining network."
        },
        "es": {
            "title_template": "Priorizar la protección de {infra}",
            "description_template": "Dado el compromiso confirmado del cable, se recomienda priorizar la monitorización y protección de {infra} restante. Considerar asignar el medio marítimo aliado disponible más cercano para observar el corredor del cable. Coordinar con el operador del cable para monitorización continua de integridad.",
            "assumptions": [
                "La infraestructura secundaria aún no ha sido comprometida",
                "El medio aliado más cercano puede llegar a la zona en 90 minutos",
                "El operador del cable puede proporcionar estado continuo de integridad"
            ],
            "expected_effect_template": "Reducción del riesgo de nuevo compromiso sobre {infra}",
            "objective_template": "Proteger {infra} restante frente a nuevas disrupciones.",
            "rationale_template": "Se selecciona porque el compromiso confirmado de infraestructura desplaza la prioridad hacia la protección de la red restante."
        },
        "fr": {
            "title_template": "Prioriser la Protection de {infra}",
            "description_template": "Compte tenu du compromis de câble confirmé, recommander de prioriser la surveillance et la protection des {infra} restants. Envisager d'affecter l'actif maritime allié le plus proche pour observer le corridor du câble. Coordonner avec l'opérateur de câble pour une surveillance continue de l'intégrité.",
            "assumptions": [
                "L'infrastructure secondaire n'a pas encore été compromise",
                "L'actif allié le plus proche peut atteindre la zone dans les 90 minutes",
                "L'opérateur de câble peut fournir un statut d'intégrité continu"
            ],
            "expected_effect_template": "Réduction du risque de compromission supplémentaire de {infra}",
            "objective_template": "Protéger les {infra} restants contre toute perturbation ultérieure.",
            "rationale_template": "Sélectionné car le compromis d'infrastructure confirmé déplace la priorité vers la protection du réseau restant."
        },
        "de": {
            "title_template": "Schutz von {infra} priorisieren",
            "description_template": "Angesichts der bestätigten Kabelkompromittierung wird empfohlen, die Überwachung und den Schutz der verbleibenden {infra} zu priorisieren. Ziehen Sie in Betracht, das nächstgelegene verfügbare alliierte maritime Asset zur Beobachtung des Kabelkorridors einzusetzen. Koordiniert mit dem Kabelbetreiber zur kontinuierlichen Integritätsüberwachung.",
            "assumptions": [
                "Die sekundäre Infrastruktur wurde noch nicht kompromittiert",
                "Das nächstgelegene alliierte Asset kann das Gebiet innerhalb von 90 Minuten erreichen",
                "Der Kabelbetreiber kann den kontinuierlichen Integritätsstatus bereitstellen"
            ],
            "expected_effect_template": "Reduziertes Risiko weiterer Kompromittierung von {infra}",
            "objective_template": "Schutz der verbleibenden {infra} vor weiteren Störungen.",
            "rationale_template": "Ausgewählt, da die bestätigte Infrastrukturkompromittierung die Priorität auf den Schutz des verbleibenden Netzwerks verschiebt."
        },
        "it": {
            "title_template": "Dare Priorità alla Protezione di {infra}",
            "description_template": "Dato il compromesso confermato del cavo, si raccomanda di dare priorità al monitoraggio e alla protezione delle rimanenti {infra}. Considerare l'assegnazione dell'asset marittimo alleato più vicino per osservare il corridoio del cavo. Coordinare con l'operatore del cavo per un monitoraggio continuo dell'integrità.",
            "assumptions": [
                "L'infrastruttura secondaria non è ancora stata compromessa",
                "L'asset alleato più vicino può raggiungere l'area entro 90 minuti",
                "L'operatore del cavo può fornire lo stato di integrità continuo"
            ],
            "expected_effect_template": "Riduzione del rischio di ulteriore compromissione di {infra}",
            "objective_template": "Proteggere le rimanenti {infra} da ulteriori interruzioni.",
            "rationale_template": "Selezionato perché il compromesso confermato dell'infrastruttura sposta la priorità verso la protezione della rete rimanente."
        },
        "pt": {
            "title_template": "Priorizar a Proteção de {infra}",
            "description_template": "Dado o comprometimento confirmado do cabo, recomenda-se priorizar o monitoramento e a proteção da {infra} restante. Considerar designar o ativo marítimo aliado mais próximo para observar o corredor do cabo. Coordenar com o operador do cabo para monitoramento contínuo da integridade.",
            "assumptions": [
                "A infraestrutura secundária ainda não foi comprometida",
                "O ativo aliado mais próximo pode alcançar a área em 90 minutos",
                "O operador do cabo pode fornecer status de integridade contínuo"
            ],
            "expected_effect_template": "Redução do risco de comprometimento adicional da {infra}",
            "objective_template": "Proteger a {infra} restante contra interrupções subsequentes.",
            "rationale_template": "Selecionado porque o comprometimento confirmado da infraestrutura muda a prioridade para proteger a rede restante."
        },
        "nl": {
            "title_template": "Prioriteer Bescherming van {infra}",
            "description_template": "Gezien de bevestigde kabelcompromittering, wordt aanbevolen om de monitoring en bescherming van de resterende {infra} te prioriteren. Overweeg het toewijzen van het dichtstbijzijnde beschikbare geallieerde maritieme middel om de kabelcorridor te observeren. Coördineren met de kabeloperator voor continue integriteitsmonitoring.",
            "assumptions": [
                "Secundaire infrastructuur is nog niet gecompromitteerd",
                "Het dichtstbijzijnde geallieerde middel kan het gebied binnen 90 minuten bereiken",
                "De kabeloperator kan continue integriteitsstatus verstrekken"
            ],
            "expected_effect_template": "Verminderd risico op verdere compromittering van {infra}",
            "objective_template": "Beschermen van de resterende {infra} tegen verdere verstoring.",
            "rationale_template": "Gekozen omdat de bevestigde infrastructuurcompromittering de prioriteit verschuift naar het beschermen van het resterende netwerk."
        },
        "pl": {
            "title_template": "Priorytetyzacja Ochrony {infra}",
            "description_template": "Biorąc pod uwagę potwierdzone naruszenie kabla, rekomenduje się priorytetowe monitorowanie i ochronę pozostałej infrastruktury {infra}. Rozważyć przydzielenie najbliższego dostępnego sojuszniczego zasobu morskiego do obserwacji korytarza kabla. Koordynować z operatorem kabla ciągłe monitorowanie integralności.",
            "assumptions": [
                "Infrastruktura wtórna nie została jeszcze naruszona",
                "Najbliższy sojuszniczy zasób może dotrzeć do obszaru w ciągu 90 minut",
                "Operator kabla może zapewnić ciągły status integralności"
            ],
            "expected_effect_template": "Zmniejszenie ryzyka dalszego naruszenia {infra}",
            "objective_template": "Ochrona pozostałej infrastruktury {infra} przed dalszym zakłóceniem.",
            "rationale_template": "Wybrano, ponieważ potwierdzone naruszenie infrastruktury zmienia priorytet na ochronę pozostałej sieci."
        },
        "tr": {
            "title_template": "{infra}'nın Korunmasına Öncelik Verin",
            "description_template": "Onaylanmış kablo ihlali göz önüne alındığında, kalan {infra}'nın izlenmesine ve korunmasına öncelik verilmesini tavsiye eder. Kablo koridorunu gözlemlemek için en yakın mevcut müttefik deniz varlığının atanmasını düşünün. Sürekli bütünlük izlemesi için kablo operatörü ile koordinasyon sağlayın.",
            "assumptions": [
                "İkincil altyapı henüz ihlal edilmedi",
                "En yakın müttefik varlık bölgeye 90 dakika içinde ulaşabilir",
                "Kablo operatörü sürekli bütünlük durumu sağlayabilir"
            ],
            "expected_effect_template": "{infra}'ya yönelik daha fazla ihlal riskinin azalması",
            "objective_template": "Kalan {infra}'yı takip eden kesintilerden korumak.",
            "rationale_template": "Seçildi çünkü onaylanmış altyapı ihlali, önceliği kalan ağı korumaya kaydırmaktadır."
        },
        "cs": {
            "title_template": "Prioritizovat ochranu {infra}",
            "description_template": "Vzhledem k potvrzenému kompromisu kabelu se doporučuje prioritizovat monitorování a ochranu zbývajícího {infra}. Zvážit přidělení nejbližšího dostupného spojeneckého maritimního prostředku k pozorování kabelového koridoru. Koordinovat s provozovatelem kabelu pro nepřetržité monitorování integrity.",
            "assumptions": [
                "Sekundární infrastruktura nebyla ještě kompromitována",
                "Nejbližší spojenecký prostředek může dosáhnout oblasti do 90 minut",
                "Provozovatel kabelu může poskytnout stav integrity v reálném čase"
            ],
            "expected_effect_template": "Snížení rizika dalšího kompromisu {infra}",
            "objective_template": "Ochrana zbývajícího {infra} před následným narušením.",
            "rationale_template": "Vybráno, protože potvrzený kompromis infrastruktury přesouvá prioritu na ochranu zbývající sítě."
        },
        "ro": {
            "title_template": "Prioritizarea Protecției {infra}",
            "description_template": "Având în vedere compromiterea confirmată a cablului, se recomandă prioritizarea monitorizării și protecției {infra} rămase. Luați în considerare alocarea celei mai apropiate resurse navale aliate pentru a observa coridorul cablului. Coordonați cu operatorul de cablu pentru monitorizarea continuă a integrității.",
            "assumptions": [
                "Infrastructura secundară nu a fost încă compromisă",
                "Resursa aliată cea mai apropiată poate ajunge în zonă în decurs de 90 de minute",
                "Operatorul de cablu poate furniza status de integritate continuu"
            ],
            "expected_effect_template": "Reducerea riscului de compromitere suplimentară a {infra}",
            "objective_template": "Protejarea {infra} rămase de perturbări ulterioare.",
            "rationale_template": "Selectat deoarece compromiterea confirmată a infrastructurii schimbă prioritatea către protejarea rețelei rămase."
        },
        "hu": {
            "title_template": "{infra} Védelemének Prioritizálása",
            "description_template": "A megerősített kábel sérülés miatt ajánlott prioritizálni a fennmaradó {infra} monitorozását és védelmét. Fontos megfontolni a legközelebbi rendelkezésre álló szövetséges tengeri eszköz kijelölését a kábel korridor megfigyelésére. Koordinálni a kábel operatórral a folyamatos integritás monitorozás érdekében.",
            "assumptions": [
                "A másodlagos infrastruktúra még nem sérült",
                "A legközelebbi szövetséges eszköz 90 perc alatt eljuthat a területre",
                "A kábel operatőr folyamatos integritási státuszt biztosíthat"
            ],
            "expected_effect_template": "{infra} további sérülésének kockázatának csökkentése",
            "objective_template": "Megvédeni a fennmaradó {infra} a további zavaroktól.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a megerősített infrastruktúra sérülés a prioritást a fennmaradó hálózat védelmére helyezi."
        },
        "bg": {
            "title_template": "Приоритизиране на Защитата на {infra}",
            "description_template": "Въз основа на потвърдено компрометиране на кабела, препоръчва се приоритизиране на мониторинга и защитата на останалите {infra}. Разгледайте възможността за назначаване на най-близкия наличен съюзнически морски актив за наблюдение на кабелния коридор. Координирайте с кабелния оператор за непрекъснат мониторинг на цялостността.",
            "assumptions": [
                "Вторичната инфраструктура все още не е компрометирана",
                "Най-близкият съюзнически актив може да достигне района в рамките на 90 минути",
                "Кабелният оператор може да предостави непрекъснат статус на цялостността"
            ],
            "expected_effect_template": "Намален риск от допълнително компрометиране на {infra}",
            "objective_template": "Защита на останалите {infra} от последващо нарушаване.",
            "rationale_template": "Избрано, защото потвърденото компрометиране на инфраструктурата измества приоритета към защита на останалата мрежа."
        },
        "hr": {
            "title_template": "Prioritet Za Zaštitu {infra}",
            "description_template": "S obzirom na potvrđeno kompromitiranje kabela, preporučuje se prioritetno praćenje i zaštita preostalog {infra}. Razmotriti dodjelu najbližeg dostupnog saveznog pomorskog sredstva za nadziranje kabelskog koridora. Koordinirati s operaterom kabela za kontinuirano praćenje integriteta.",
            "assumptions": [
                "Sekundarna infrastruktura još nije kompromitirana",
                "Najbliže savezno sredstvo može dosegnuti područje u roku od 90 minuta",
                "Operater kabela može pružiti kontinuirani status integriteta"
            ],
            "expected_effect_template": "Smanjenje rizika daljnjeg kompromitiranja {infra}",
            "objective_template": "Zaštititi preostali {infra} od daljnjeg poremećaja.",
            "rationale_template": "Odabrano jer potvrđeno kompromitiranje infrastrukture mijenja prioritet prema zaštiti preostale mreže."
        },
        "sk": {
            "title_template": "Prioritizovať ochranu {infra}",
            "description_template": "Vzhľadom na potvrdené narušenie kábla odporúča sa prioritizovať monitorovanie a ochrana zvyšného {infra}. Zvážiť pridelenie najbližšieho dostupného spojeneckého morského aktívu na sledovanie kábelového koridoru. Koordinovať s operatérom kábla pre nepretržitý monitorovací stav integritety.",
            "assumptions": [
                "Sekundárna infraštruktúra ešte nebola narušená",
                "Najbližšie spojenecké aktívum môže dosiahnuť oblasť do 90 minút",
                "Operátor kábla môže poskytnúť nepretržitý stav integritety"
            ],
            "expected_effect_template": "Znížený riziko ďalšieho narušenia {infra}",
            "objective_template": "Chrániť zvyšné {infra} pred následným narušením.",
            "rationale_template": "Vybrané, pretože potvrdené narušenie infraštruktúry zmení prioritu na ochranu zvyšnej siete."
        },
        "sl": {
            "title_template": "Prioritizacija zaščite {infra}",
            "description_template": "Glede na potrjeno kompromitacijo kabla se priporoča prioritetno spremljanje in zaščita preostalih {infra}. Razmislite o dodelitvi najbližjega zavezniškega pomorskega sredstva za opažanje kablorskega koridora. Koordinirajte z operatorjem kabla za neprekinjeno spremljanje integritete.",
            "assumptions": [
                "Sekundarna infrastruktura še ni kompromitirana",
                "Najbližje zavezniško sredstvo lahko doseže območje v roku 90 minut",
                "Operator kabla lahko zagotovi neprekinjen status integritete"
            ],
            "expected_effect_template": "Zmanjšanje tveganja nadaljnje kompromitacije {infra}",
            "objective_template": "Zaščititi preostalo {infra} pred nadaljnjo motnjavo.",
            "rationale_template": "Izbrano, ker potrjena kompromitacija infrastrukture premika prioriteto na zaščito preostale mreže."
        },
        "et": {
            "title_template": "Prioriteetne {infra} kaitse",
            "description_template": "Vastavalt kinnitatud kaabli kompromitatsioonile soovitatakse prioriteetne jälgimine ja kaitse jäljepõhjustatud {infra}. Kaaluge määrata lähim olemasolev liitaste mereliste vara kaabli koridori jälgimiseks. Koordineerige kaabli operatiiviga pideva terviklikkuse jälgimise saamiseks.",
            "assumptions": [
                "Sekundaarne infrastruktuur ei ole veel kompromiteeritud",
                "Lähim liitaste vara saab jõuda alale 90 minuti jooksul",
                "Kaabli operatiiv võib pakkuda pidevat terviklikkuse staatust"
            ],
            "expected_effect_template": "Vähendatud risk {infra} edasese kompromitatsioonile",
            "objective_template": "Kaitseda jäljepõhjustatud häirumisest {infra}.",
            "rationale_template": "Valitud, sest kinnitatud infrastruktuuri kompromitatsioon viib prioriteeti jäljepõhjustatud võrgu kaitseks."
        },
        "lv": {
            "title_template": "Prioritizēt {infra} aizsardzību",
            "description_template": "Ņemot vērā apstiprināto kabela kompromitāciju, ieteicams prioritizēt atlikušās {infra} uzraudzību un aizsardzību. Ap慮tīt apzīmēt tuvāko pieejamo alliēšu jūras resursu, lai observētu kabela koridoru. Koordinēt ar kabela operatoriem, lai nodrošinātu nepārtrauktu integritātes uzraudzību.",
            "assumptions": [
                "Sekundārais infrastruktūra vēl nav kompromitēts",
                "Tuvākais alliēšu resurs var sasniegt teritoriju 90 minūtu laikā",
                "Kabela operators var nodrošināt nepārtrauktu integritātes statusu"
            ],
            "expected_effect_template": "Samazināts riska līmenis papildu kompromitācijai {infra}",
            "objective_template": "Aizsargāt atlikušo {infra} no turpmākās traucējuma.",
            "rationale_template": "Izvēlēts, jo apstiprināta infrastruktūras kompromitācija pārvieto prioritāti uz atlikušās tīkla aizsardzību."
        },
        "lt": {
            "title_template": "Prioritetizuoti {infra} Apsaugą",
            "description_template": "Dėl patvirtinto kabelio pažeidimo regaliam prioritetizuoti stebėjimą ir {infra} likusio apsaugą. Svarbu apsvaryti paskirstyti artimiausią prieinamą alysių jūrinį išteklį stebėti kabelio koridorą. Koordinuoti su kabelio operatoriais dėl nuolatinio vientisumo stebėjimo.",
            "assumptions": [
                "Antrinė infrastruktūra dar nepažeista",
                "Artimiausias alysių išteklis gali pasiekti šią vietą per 90 minučių",
                "Kabelio operatorius gali pateikti nuolatinį vientisumo statusą"
            ],
            "expected_effect_template": "Sumažintas rizikos pažeidimo {infra} toliau",
            "objective_template": "Apsaugoti likusią {infra} nuo toliau esančio sutrikimo.",
            "rationale_template": "Pasirinkta, nes patvirtintas infrastruktūros pažeidimas keičia prioritetą į likusios tinklo apsaugą."
        },
        "da": {
            "title_template": "Prioriter Beskyttelse af {infra}",
            "description_template": "Givet bekræftet kabelkompromittering, anbefales det at prioritere overvågning og beskyttelse af den resterende {infra}. Overvej at tildele det nærmeste tilgængelige allierede maritime aktiv til at observere kabelkorridoren. Koordiner med kabeloperatøren for kontinuerlig integritetsmonitorering.",
            "assumptions": [
                "Sekundær infrastruktur er endnu ikke kompromitteret",
                "Nærmeste allierede aktiv kan nå området inden for 90 minutter",
                "Kabeloperatøren kan give kontinuerlig integritetsstatus"
            ],
            "expected_effect_template": "Reduceret risiko for yderligere kompromittering af {infra}",
            "objective_template": "Beskyt den resterende {infra} mod efterfølgende forstyrrelse.",
            "rationale_template": "Valgt, fordi bekræftet infrastrukturkompromittering skifter prioriteten mod at beskytte det resterende netværk."
        },
        "no": {
            "title_template": "Prioriter beskyttelse av {infra}",
            "description_template": "Gitt bekreftet kabelkompromiss, anbefales det å prioritere overvåking og beskyttelse av gjenværende {infra}. Vurder å tildele nærmeste tilgjengelige allierte maritime ressurs for å observere kabelkorridoren. Koordinere med kabeloperatøren for kontinuerlig integritetsmonitorering.",
            "assumptions": [
                "Sekundær infrastruktur er ennå ikke kompromittert",
                "Nærmeste allierte ressurs kan nå området innen 90 minutter",
                "Kabeloperatøren kan gi kontinuerlig integritetsstatus"
            ],
            "expected_effect_template": "Redusert risiko for ytterligere kompromiss av {infra}",
            "objective_template": "Beskytte gjenværende {infra} mot oppfølgende forstyrrelser.",
            "rationale_template": "Valgt fordi bekreftet infrastrukturkompromiss flytter prioriteringen mot å beskytte det gjenværende nettverket."
        },
        "is": {
            "title_template": "Fyrirrangsla verndar á {infra}",
            "description_template": "Þar sem staðfest skemmdir á kebla eru til staðar, mætir með að gefa forgang á eftirlit og vernd á eftirfarandi {infra}. Horfa á að neita næstu til staðandi samstarfandi sjóauðlind til að eftirlita kebla gangbrautinni. Samræmd við kebla aðila fyrir stöðugt eftirlit á heilbrigði.",
            "assumptions": [
                "Íkinfrastruktúran hefur ekki verið skemmd ennþá",
                "Næstu samstarfandi auðlind getur náið svæðinu innan 90 mínútum",
                "Kebla aðili getur veitt stöðugt staðreyndar um heilbrigði"
            ],
            "expected_effect_template": "Minnta hættu á frekari skemmdum á {infra}",
            "objective_template": "Vernda eftirfarandi {infra} frá eftirfarandi störfum.",
            "rationale_template": "Valinn því að staðfest skemmdir á infrastruktúru breyta forgangi til að vernda eftirfarandi netverk."
        },
        "fi": {
            "title_template": "Priorisoi {infra}:n suojaaminen",
            "description_template": "Vahvistetun kaapelivaurion perusteella suositellaan priorisoida jäljellä olevan {infra}:n seuranta ja suojaaminen. Harkitaan lähimmän saatavilla olevan liittoutuneen merivarusteen osoittamista kaapelikoridorin havainnoinnin vuoksi. Koordinoi kaapelitoimijan kanssa jatkuvan eheyden seurannan varmistamiseksi.",
            "assumptions": [
                "Toissijainen infrastruktuuri ei ole vielä vioittunut",
                "Lähin liittoutunut varuste voi saavuttaa alueen 90 minuutissa",
                "Kaapelitoimija voi tarjota jatkuvan eheyden tilan"
            ],
            "expected_effect_template": "Vähentynyt riski lisävaurioille {infra}:lle",
            "objective_template": "Suojaa jäljellä olevaa {infra} seuraavien häiriöiden vaikutukselta.",
            "rationale_template": "Valittu, koska vahvistettu infrastruktuurin vaurio siirtää prioriteetin jäljellä olevan verkon suojaamiseen."
        },
        "sv": {
            "title_template": "Prioritera skydd av {infra}",
            "description_template": "Med bekräftad kabelkompromiss rekommenderas prioritering av övervakning och skydd av återstående {infra}. Överväg att tilldela den närmaste tillgängliga allierade sjötillgången för att observera kabelkorridoren. Koordinera med kabeloperatören för kontinuerlig integritetsövervakning.",
            "assumptions": [
                "Sekundär infrastruktur har ännu inte komprometterats",
                "Närmaste allierade tillgången kan nå området inom 90 minuter",
                "Kabeloperatören kan tillhandahålla kontinuerlig integritetsstatus"
            ],
            "expected_effect_template": "Minskad risk för ytterligare kompromiss till {infra}",
            "objective_template": "Skydda återstående {infra} från efterföljande störningar.",
            "rationale_template": "Vald eftersom bekräftad infrastrukturkompromiss skiftar prioriteringen mot att skydda det återstående nätverket."
        },
        "sq": {
            "title_template": "Prioritizoni Mbrojtjen e {infra}",
            "description_template": "Duke pasur në dorë komprometimin e konfirmuar të kabllos, rekomandojmë prioritizimin e monitorimit dhe mbrojtjes së {infra} të mbetur. Konsideroni caktimin e asetusit detar më të afërt të aleatëve për të vëzhguar korridorin e kabllos. Koordinoni me operatorin e kabllos për monitorim të vazhdueshëm të integritetit.",
            "assumptions": [
                "Infrastruktura sekondare ende nuk është komprometuar",
                "Aseti më i afërt i aleatëve mund të arrijë në zonë brenda 90 minutash",
                "Operatori i kabllos mund të ofrojë status të vazhdueshëm të integritetit"
            ],
            "expected_effect_template": "Rrezik i ulur i komprometimit të mëtejshëm të {infra}",
            "objective_template": "Mbrojtja e {infra} të mbetur nga ndërprerjet e mëtejshme.",
            "rationale_template": "Zgjedhur sepse komprometimi i konfirmuar i infrastrukturës zhvendos prioritetin drejt mbrojtjes së rrjetit të mbetur."
        },
        "mk": {
            "title_template": "Приоритизирање на заштита на {infra}",
            "description_template": "Со потврдено компромитирање на кабелот, препорачуваме да се даде приоритет на следењето и заштитата на преостанатиот {infra}. Размислете за доделување на најблискиот достапен сојузен морски актив за следење на коридорот на кабелот. Координирајте со операторот на кабелот за континуирано следење на интегритетот.",
            "assumptions": [
                "Вторичната инфраструктура сè уште не е компромитирана",
                "Најблискиот сојузен актив може да стигне во областа во рок од 90 минути",
                "Операторот на кабелот може да обезбеди континуиран статус на интегритетот"
            ],
            "expected_effect_template": "Намален ризик од дополнително компромитирање на {infra}",
            "objective_template": "Заштита на преостанатиот {infra} од дополнителни прекини.",
            "rationale_template": "Избрано бидејќи потврдено компромитирање на инфраструктурата го менува приоритетот кон заштита на претставната мрежа."
        },
        "me": {
            "title_template": "Prioritet Za Zaštitu {infra}",
            "description_template": "S obzirom na potvrđeni kompromit kabla, preporučuje se da se prioritet odredi za nadzor i zaštitu preostalog {infra}. Razmotriti dodeljivanje najbližeg dostupnog saveznog morskog sredstva za nadzor kablovskog koridora. Koordinirati sa operaterom kabla za kontinuirani nadzor integriteta.",
            "assumptions": [
                "Sekundarna infrastruktura još nije kompromitovana",
                "Najbliže savezno sredstvo može stići u područje u roku od 90 minuta",
                "Operater kabla može pružiti status kontinuirane integriteta"
            ],
            "expected_effect_template": "Smanjen rizik daljeg kompromitovanja {infra}",
            "objective_template": "Zaštiti preostalu {infra} od daljeg poremećaja.",
            "rationale_template": "Odabrano jer potvrđeni kompromit infrastrukture menja prioritet ka zaštiti preostale mreže."
        },
        "el": {
            "title_template": "Προτεραιοποίηση της Προστασίας του {infra}",
            "description_template": "Δεδομένης της επιβεβαιωμένης υπονόμευσης του καλωδίου, συνιστάται η προτεραιοποίηση της παρακολούθησης και της προστασίας του υπόλοιπου {infra}. Να εξεταστεί η ανάθεση του πλησιέστερου διαθέσιμου συμμαχικού θαλάσσιου περιουσιακού στοιχείου για παρακολούθηση του διαδρόμου του καλωδίου. Συντονισμός με τον τεχνικό του καλωδίου για συνεχή παρακολούθηση της ακεραιότητας.",
            "assumptions": [
                "Η δευτερεύουσα υποδομή δεν έχει ακόμη υπονόμευση",
                "Το πλησιέστερο συμμαχικό περιουσιακό στοιχείο μπορεί να φτάσει στην περιοχή εντός 90 λεπτών",
                "Ο τεχνικός του καλωδίου μπορεί να παρέχει συνεχή κατάσταση ακεραιότητας"
            ],
            "expected_effect_template": "Μειωμένος κίνδυνος περαιτέρω υπονόμευσης του {infra}",
            "objective_template": "Προστασία του υπόλοιπου {infra} από περαιτέρω διακοπή.",
            "rationale_template": "Επιλέχθηκε επειδή η επιβεβαιωμένη υπονόμευση της υποδομής μετατοπίζει την προτεραιότητα στην προστασία του υπόλοιπου δικτύου."
        }
    },
    "COA-TPL-AIRSPACE": {
        "en": {
            "title_template": "Coordinate Civilian Airspace Safety Response",
            "description_template": "Recommend coordination with civil aviation authority to manage airspace around affected area. Support establishment of temporary flight restrictions. Share available sensor data with air traffic control.",
            "assumptions": [
                "Civil aviation authority is responsive",
                "UAV does not escalate to controlled airspace breach",
                "Commercial diversions can be managed without major disruption"
            ],
            "expected_effect_template": "Safe civilian airspace management during UAV incident near {infra}",
            "objective_template": "Reduce civilian airspace disruption and improve safety around the affected area.",
            "rationale_template": "Selected because UAV activity near civilian airspace requires coordinated civil-safety management."
        },
        "es": {
            "title_template": "Coordinar respuesta de seguridad del espacio aéreo civil",
            "description_template": "Se recomienda coordinar con la autoridad de aviación civil para gestionar el espacio aéreo en torno al área afectada. Apoyar el establecimiento de restricciones temporales de vuelo. Compartir datos de sensores disponibles con el control de tráfico aéreo.",
            "assumptions": [
                "La autoridad de aviación civil responde con rapidez",
                "El UAV no escala a una intrusión en espacio aéreo controlado",
                "Los desvíos comerciales pueden gestionarse sin gran disrupción"
            ],
            "expected_effect_template": "Gestión segura del espacio aéreo civil durante un incidente UAV cerca de {infra}",
            "objective_template": "Reducir la disrupción del espacio aéreo civil y mejorar la seguridad alrededor del área afectada.",
            "rationale_template": "Se selecciona porque la actividad UAV cerca del espacio aéreo civil requiere gestión coordinada de seguridad civil."
        },
        "fr": {
            "title_template": "Coordonner la Réponse de Sécurité de l'Espace Aérien Civil",
            "description_template": "Recommander une coordination avec l'autorité de l'aviation civile pour gérer l'espace aérien autour de la zone affectée. Soutenir l'établissement de restrictions de vol temporaires. Partager les données de capteurs disponibles avec le contrôle aérien.",
            "assumptions": [
                "L'autorité de l'aviation civile est réactive",
                "Le drone n'escalade pas à une violation de l'espace aérien contrôlé",
                "Les déviations commerciales peuvent être gérées sans perturbation majeure"
            ],
            "expected_effect_template": "Gestion sûre de l'espace aérien civil pendant l'incident de drone près de {infra}",
            "objective_template": "Réduire la perturbation de l'espace aérien civil et améliorer la sécurité autour de la zone affectée.",
            "rationale_template": "Sélectionné car l'activité des drones près de l'espace aérien civil nécessite une gestion coordonnée de la sécurité civile."
        },
        "de": {
            "title_template": "Koordination der zivilen Luftraum-Sicherheitsreaktion",
            "description_template": "Empfiehlt die Koordination mit der zivilen Luftfahrtbehörde zur Verwaltung des Luftraums rund um das betroffene Gebiet. Unterstützung bei der Einrichtung temporärer Flugbeschränkungen. Teilen Sie verfügbare Sensordaten mit der Flugverkehrskontrolle.",
            "assumptions": [
                "Die zivile Luftfahrtbehörde ist reaktionsfähig",
                "Das UAV eskaliert nicht zu einem Einbruch in den kontrollierten Luftraum",
                "Kommerzielle Umleitungen können ohne größere Störungen verwaltet werden"
            ],
            "expected_effect_template": "Sichere zivile Luftraumverwaltung während eines UAV-Vorfalls in der Nähe von {infra}",
            "objective_template": "Reduzierung der Störungen im zivilen Luftraum und Verbesserung der Sicherheit rund um das betroffene Gebiet.",
            "rationale_template": "Ausgewählt, da UAV-Aktivität in der Nähe des zivilen Luftraums eine koordinierte zivil-sicherheitsrelevante Verwaltung erfordert."
        },
        "it": {
            "title_template": "Coordinare la Risposta per la Sicurezza dello Spazio Aereo Civile",
            "description_template": "Si raccomanda di coordinare con l'autorità aeronautica civile per gestire lo spazio aereo intorno all'area interessata. Supportare l'istituzione di restrizioni di volo temporanee. Condividere i dati dei sensori disponibili con il controllo del traffico aereo.",
            "assumptions": [
                "L'autorità aeronautica civile è reattiva",
                "L'UAV non scala a una violazione dello spazio aereo controllato",
                "Le deviazioni commerciali possono essere gestite senza interruzioni maggiori"
            ],
            "expected_effect_template": "Gestione sicura dello spazio aereo civile durante l'incidente UAV vicino a {infra}",
            "objective_template": "Ridurre le interruzioni dello spazio aereo civile e migliorare la sicurezza intorno all'area interessata.",
            "rationale_template": "Selezionato perché l'attività UAV vicino allo spazio aereo civile richiede una gestione coordinata della sicurezza civile."
        },
        "pt": {
            "title_template": "Coordenar a Resposta de Segurança do Espaço Aéreo Civil",
            "description_template": "Recomenda-se a coordenação com a autoridade de aviação civil para gerenciar o espaço aéreo ao redor da área afetada. Apoiar o estabelecimento de restrições de voo temporárias. Compartilhar dados de sensores disponíveis com o controle de tráfego aéreo.",
            "assumptions": [
                "A autoridade de aviação civil é responsiva",
                "O UAV não escala para violação do espaço aéreo controlado",
                "Desvios comerciais podem ser gerenciados sem grande interrupção"
            ],
            "expected_effect_template": "Gerenciamento seguro do espaço aéreo civil durante incidente de UAV perto de {infra}",
            "objective_template": "Reduzir a interrupção do espaço aéreo civil e melhorar a segurança ao redor da área afetada.",
            "rationale_template": "Selecionado porque a atividade de UAV perto do espaço aéreo civil requer gerenciamento coordenado de segurança civil."
        },
        "nl": {
            "title_template": "Coördineer Civiele Luchtruimte Veiligheidsrespons",
            "description_template": "Aanbeveling tot coördinatie met de civiele luchtvaartautoriteit om de luchtruimte rond het getroffen gebied te beheren. Ondersteunen bij het vaststellen van tijdelijke vluchtbeperkingen. Delen van beschikbare sensordata met de luchtverkeersleiding.",
            "assumptions": [
                "De civiele luchtvaartautoriteit is responsief",
                "De UAV escaleert niet naar een inbreuk op de gecontroleerde luchtruimte",
                "Commerciële omleidingen kunnen worden beheerd zonder grote verstoring"
            ],
            "expected_effect_template": "Veilig civiele luchtruimtebeheer tijdens UAV-incident nabij {infra}",
            "objective_template": "Verminderen van civiele luchtruimteverstoring en verbeteren van de veiligheid rond het getroffen gebied.",
            "rationale_template": "Gekozen omdat UAV-activiteit nabij civiele luchtruimte gecombineerd civiel-veiligheidsbeheer vereist."
        },
        "pl": {
            "title_template": "Koordynacja Reakcji Bezpieczeństwa Przestrzeni Powietrznej Cywilnej",
            "description_template": "Rekomenduje się koordynację z cywilnym organem lotniczym w celu zarządzania przestrzenią powietrzną wokół dotkniętego obszaru. Wsparcie ustanowienia tymczasowych ograniczeń lotów. Udostępnianie dostępnych danych czujników kontroli ruchu lotniczego.",
            "assumptions": [
                "Cywilny organ lotniczy jest reaktywny",
                "UAV nie eskaluje do naruszenia kontrolowanej przestrzeni powietrznej",
                "Przekierowania komercyjne mogą być zarządzane bez poważnych zakłóceń"
            ],
            "expected_effect_template": "Bezpieczne zarządzanie przestrzenią powietrzną cywilną podczas incydentu UAV w pobliżu {infra}",
            "objective_template": "Zmniejszenie zakłóceń w przestrzeni powietrznej cywilnej i poprawa bezpieczeństwa wokół dotkniętego obszaru.",
            "rationale_template": "Wybrano, ponieważ aktywność UAV w pobliżu przestrzeni powietrznej cywilnej wymaga skoordynowanego zarządzania bezpieczeństwem cywilnym."
        },
        "tr": {
            "title_template": "Sivil Hava Sahası Güvenlik Yanıtını Koordinasyon",
            "description_template": "Etkilenen bölge çevresindeki hava sahasını yönetmek için sivil havacılık otoritesi ile koordinasyon sağlamayı tavsiye eder. Geçici uçuş kısıtlamalarının kurulmasına destek olun. Mevcut sensör verilerini hava trafik kontrolü ile paylaşın.",
            "assumptions": [
                "Sivil havacılık otoritesi yanıt veriyor",
                "UAV kontrollü hava sahası ihlaline tırmanmıyor",
                "Ticari yönlendirmeler büyük bir aksaklık olmadan yönetilebilir"
            ],
            "expected_effect_template": "{infra} yakınındaki UAV olayı sırasında güvenli sivil hava sahası yönetimi",
            "objective_template": "Sivil hava sahası aksaklığını azaltmak ve etkilenen bölge çevresinde güvenliği artırmak.",
            "rationale_template": "Seçildi çünkü sivil hava sahası yakınındaki UAV faaliyeti koordineli sivil-güvenlik yönetimi gerektirir."
        },
        "cs": {
            "title_template": "Koordinovat reakci na bezpečnost civilního vzdušného prostoru",
            "description_template": "Doporučuje se koordinovat s civilní leteckou autoritou pro řízení vzdušného prostoru v okolí dotčeného obszaru. Podpořit zavedení dočasných omezení letu. Sdílet dostupné senzory data s řízením letového provozu.",
            "assumptions": [
                "Civilní letecká autorita je reaktivní",
                "UAV neeskaluje k porušení kontrolovaného vzdušného prostoru",
                "Komerční přesměrování lze zvládnout bez velkého narušení"
            ],
            "expected_effect_template": "Bezpečné řízení civilního vzdušného prostoru během incidentu UAV poblíž {infra}",
            "objective_template": "Snížit narušení civilního vzdušného prostoru a zlepšit bezpečnost v okolí dotčeného obszaru.",
            "rationale_template": "Vybráno, protože činnost UAV v blízkosti civilního vzdušného prostoru vyžaduje koordinované řízení civilní bezpečnosti."
        },
        "ro": {
            "title_template": "Coordonarea Răspunsului pentru Siguranța Spațiului Aerian Civil",
            "description_template": "Se recomandă coordonarea cu autoritatea de aviație civilă pentru gestionarea spațiului aerian în jurul zonei afectate. Susțineți stabilirea restricțiilor temporare de zbor. Distribuiți datele senzoriale disponibile către controlul traficului aerian.",
            "assumptions": [
                "Autoritatea de aviație civilă este responsivă",
                "UAV nu escaladează la o încălcare a spațiului aerian controlat",
                "Devierele comerciale pot fi gestionate fără perturbări majore"
            ],
            "expected_effect_template": "Gestionarea sigură a spațiului aerian civil în timpul incidentului UAV în apropierea {infra}",
            "objective_template": "Reducerea perturbărilor spațiului aerian civil și îmbunătățirea siguranței în jurul zonei afectate.",
            "rationale_template": "Selectat deoarece activitatea UAV în apropierea spațiului aerian civil necesită o gestionare coordonată civil-siguranță."
        },
        "hu": {
            "title_template": "Polgári Légi Terület Biztonsági Válasz Koordinálása",
            "description_template": "Ajánlott koordinálni a polgári légi felügyeletügyelmedéssel a sérült terület körüli légi térség kezeléséhez. Támogatni a ideiglenes repülési korlátozások létrehozását. Megosztani a rendelkezésre álló szenzoradatokat a légi forgalom irányításúval.",
            "assumptions": [
                "A polgári légi felügyeletügyelem reagál",
                "A UAV nem eskalál kontrollált légi térség behatolásához",
                "A kereskedelmi eltérek kezelhetők anélkül, hogy jelentős zavar keletkezne"
            ],
            "expected_effect_template": "Biztonságos polgári légi térség kezelése a UAV esemény alatt a {infra} közelében",
            "objective_template": "Csökkenteni a polgári légi térség zavarát és javítani a biztonságot a sérült terület körül.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a UAV tevékenysége a polgári légi térség közelében koordinált polgári-biztonsági kezelést igényel."
        },
        "bg": {
            "title_template": "Координация на Отговор за Безопасност на Гражданското Въздушно Пространство",
            "description_template": "Препоръчва се координация с гражданския авиационен орган за управление на въздушното пространство около засегнатата зона. Подкрепа за установяване на временни ограничения за полети. Споделяне на наличните сензорни данни с контрола на движението в небето.",
            "assumptions": [
                "Гражданският авиационен орган е отзивчив",
                "UAV не ескалира до нарушение на контролирано въздушно пространство",
                "Комерсиалните отклонения могат да бъдат управлявани без сериозно нарушение"
            ],
            "expected_effect_template": "Безопасно управление на гражданското въздушно пространство по време на инцидент с UAV близо до {infra}",
            "objective_template": "Намаляване на нарушаването на гражданското въздушно пространство и подобряване на безопасността около засегнатата зона.",
            "rationale_template": "Избрано, защото дейността на UAV близо до гражданското въздушно пространство изисква координирано гражданско-безопасно управление."
        },
        "hr": {
            "title_template": "Koordinacija Odgovora za Sigurnost Civilnog Prostranstva",
            "description_template": "Preporučuje se koordinacija s civilnom aviacijskom vlasti za upravljanje zračnim prostorom oko zahvaćenog područja. Podržati uspostavljanje privremenih ograničenja leta. Podijeliti dostupne senzorske podatke s kontrolom zračnog prometa.",
            "assumptions": [
                "Civilna aviacijska vlast je reaktywna",
                "UAV ne eskalira do kršenja kontroliranog zračnog prostora",
                "Komercijalna preusmjeravanja mogu se upravljati bez velikih poremećaja"
            ],
            "expected_effect_template": "Sigurno upravljanje civilnim zračnim prostorom tijekom incidenta UAV-a u blizini {infra}",
            "objective_template": "Smanjiti poremećaj civilnog zračnog prostora i poboljšati sigurnost oko zahvaćenog područja.",
            "rationale_template": "Odabrano jer aktivnosti UAV-a u blizini civilnog zračnog prostora zahtijevaju koordinirano upravljanje civilnom sigurnošću."
        },
        "sk": {
            "title_template": "Koordinovať reakciu na bezpečnosť civilného vzdušného priestoru",
            "description_template": "Odporúča sa koordinovať s civilnou leteckou autoritou na riadenie vzdušného priestoru okolo ovplyvnenej oblasti. Podporovať zriadenie dočasných obmedzení letu. Zdieľať dostupné senzorové dáta s vzdušným riadením.",
            "assumptions": [
                "Civilná letecká autorita je reaktívna",
                "UAV sa neeskaluje na narušenie kontrolovaného vzdušného priestoru",
                "Komerčné presmerovania sa môžu riadiť bez hlavného narušenia"
            ],
            "expected_effect_template": "Bezpečné riadenie civilného vzdušného priestoru počas incidentu UAV blízko {infra}",
            "objective_template": "Znížiť narušenie civilného vzdušného priestoru a zlepšiť bezpečnosť okolo ovplyvnenej oblasti.",
            "rationale_template": "Vybrané, pretože činnosť UAV blízko civilného vzdušného priestoru vyžaduje koordinované civilno-bezpečnostné riadenie."
        },
        "sl": {
            "title_template": "Koordinacija odziva za varnost civilnega zračnega prostora",
            "description_template": "Priporoča se koordinacija z civilno aviacijsko uradnostjo za upravljanje zračnega prostora okoli vplivanega območja. Podpora ustanovitvi začasnih omejitev leta. Deljenje dostopnih senzornih podatkov z nadzorom zračnega prometa.",
            "assumptions": [
                "Civilna aviacijska uradnost je odzivna",
                "UAV ne eskalira do kršitve kontrolovanega zračnega prostora",
                "Trgovinske preusmeritve se lahko upravljajo brez večjih motenj"
            ],
            "expected_effect_template": "Varna upravitev civilnega zračnega prostora med UAV incidentom blizu {infra}",
            "objective_template": "Zmanjšanje motenj civilnega zračnega prostora in izboljšanje varnosti okoli vplivanega območja.",
            "rationale_template": "Izbrano, ker dejavnost UAV blizu civilnega zračnega prostora zahteva koordinirano civilno-varnostno upravljanje."
        },
        "et": {
            "title_template": "Koordineerige tsiviililennutuste turvalisuse vastus",
            "description_template": "Soovitatakse koordineerida tsiviililennutuste väljastaja kanssa mõjutatud ala ilmaturu haldamiseks. Toetada ajutiste lennõiguspiirkondade asutamist. Jagada olemasoleva andurdata lennuliikluskontrolliga.",
            "assumptions": [
                "Tsiviililennutuste väljastaja on reageeriv",
                "UAV ei eskale kontrollitud ilmaturu rikkumiseks",
                "Kaubanduslikud kõrvalviidud saab hallata ilma suurte häirumiseta"
            ],
            "expected_effect_template": "Turvaline tsiviililennutuste haldamine UAV insidentsi ajal {infra} läheduses",
            "objective_template": "Vähendada tsiviililennutuste häirumist ja parandada turvalisust mõjutatud ala ümber.",
            "rationale_template": "Valitud, sest UAV tegevus tsiviililennutuste läheduses nõuab koordineeritud tsiviil-turvalisuse haldamist."
        },
        "lv": {
            "title_template": "Koordinēt civilās gaisa telpas drošības reakciju",
            "description_template": "Ieteicams koordinēt ar civilās aviācijas iestādes, lai vadītu gaisa telpu apiet šo teritoriju. Atbalstīt provizoriskajām vilciens ierobežojumiem. Dalīties pieejamajiem sensora datiem ar gaisa trafika vadību.",
            "assumptions": [
                "Civilās aviācijas iestāde ir reaģējoša",
                "UAV neuzstiprinās līdz kontrollētai gaisa telpas pārkāpumam",
                "Komerciālie novirzījumi var tiekties vadīti bez lielām traucējumiem"
            ],
            "expected_effect_template": "Droša civilās gaisa telpas vadība UAV incidenta laikā tuvumā {infra}",
            "objective_template": "Samazināt civilās gaisa telpas traucējumus un uzlabot drošību apiet šo teritoriju.",
            "rationale_template": "Izvēlēts, jo UAV aktivitāte civilās gaisa telpās prasa koordinētu civilo-drošības vadību."
        },
        "lt": {
            "title_template": "Koordinuoti Civilinės Gaisro Taisymo Atsakymą",
            "description_template": "Regaliam koordinuoti su civilinės aviacijos autoritetu, kad valdytų orotyjį aplinkafjektuotą vietą. Padėti įgyvendinti laikinas skrydymo apribojimus. Dalintis prieinamais sensorių duomenimis su oro eismo kontroliu.",
            "assumptions": [
                "Civilinės aviacijos autoritetas yra atsakingas",
                "UAV neeskaluoja iki kontroliuojamo orotyje pažeidimo",
                "Komerciniai nukreipimai gali būti valdomi be didelio sutrikimo"
            ],
            "expected_effect_template": "Saugus civilinis orotyje valdymas UAV incidento metu prie {infra}",
            "objective_template": "Sumažinti civilinio orotyje sutrikimą ir pagerinti saugumą aplinkafjektuotai vietai.",
            "rationale_template": "Pasirinkta, nes UAV veikla civilinio orotyje aplinkafjektuotai vietai reikalauja koordinuoto civilinės saugos valdymo."
        },
        "da": {
            "title_template": "Koordiner Civilt Luftrumssikkerhedsrespons",
            "description_template": "Anbefaler koordinering med civil luftfartsmyndighed for at styre luftrummet omkring det berørte område. Støt etableringen af midlertidige flyrestriktioner. Del tilgængelige sensordata med lufttrafikkontrollen.",
            "assumptions": [
                "Civil luftfartsmyndighed er responsiv",
                "UAV eskalerer ikke til brud på kontrolleret luftrum",
                "Kommercielle omdirigeringer kan håndteres uden større forstyrrelse"
            ],
            "expected_effect_template": "Sikker civil luftrumsstyring under UAV-hændelse nær {infra}",
            "objective_template": "Reducer civil luftrumsstøj og forbedr sikkerheden omkring det berørte område.",
            "rationale_template": "Valgt, fordi UAV-aktivitet nær civil luftrum kræver koordineret civil-sikkerhedsstyring."
        },
        "no": {
            "title_template": "Koordinere respons for sivil luftromssikkerhet",
            "description_template": "Anbefaler koordinering med sivil luftfartsmyndighet for å håndtere luftrommet rundt det berørte området. Støtte etablering av midlertidige flyrestriksjoner. Dele tilgjengelige sensordata med lufttrafikkontrollen.",
            "assumptions": [
                "Sivil luftfartsmyndighet er responsiv",
                "UAV eskalerer ikke til kontrollert luftromsbrudd",
                "Kommersielle omdirigeringer kan håndteres uten større forstyrrelse"
            ],
            "expected_effect_template": "Trygg sivil luftromsstyring under UAV-hendelse nær {infra}",
            "objective_template": "Redusere forstyrrelser i sivil luftrom og forbedre sikkerheten rundt det berørte området.",
            "rationale_template": "Valgt fordi UAV-aktivitet nær sivil luftrom krever koordinert sivil-sikkerhetsstyring."
        },
        "is": {
            "title_template": "Samræma áferð á borgarflugsvæði",
            "description_template": "Mætir með samræmingu við borgarflugvísindastjórn til að stjórna flugsvæði um svæðið. Styrkja stofnun tímabundna flugrestriktaka. Deila til staðandi sensorupplýsingum með flugrafíkrafstjórn.",
            "assumptions": [
                "Borgarflugvísindastjórn er ábyrgðar",
                "UAV aukar ekki til stjórnaðs flugsvæðis brot",
                "Kaupmannalega umleiðingar geta verið stjórnaðar án stórar störk"
            ],
            "expected_effect_template": "Söður borgarflugsvæðisstjórnun við UAV-eiga í nærleika {infra}",
            "objective_template": "Minnta borgarflugsvæðisstörk og bæta öryggi um svæðið.",
            "rationale_template": "Valinn því að UAV-virkni í nærleika borgarflugsvæðis krefst samræmdar borgar-öryggisstjórnunar."
        },
        "fi": {
            "title_template": "Koordinoi siviiliilmatilan turvallisuusvastuu",
            "description_template": "Suositellaan koordinaatiota siviiliilmailuviranomaisen kanssa ilmatilan hallinnoimiseksi vaikutusalueella. Tukee väliaikaisten lentorajoitusten asettamista. Jaa saatavilla oleva sensordata lentokoneohjaukseen.",
            "assumptions": [
                "Siviiliilmailuviranomainen on reagoiva",
                "UAV ei eskaloitu hallittuun ilmatilaan loukkaukseksi",
                "Kaupalliset ohjaukset voidaan hallita ilman suurta häiriötä"
            ],
            "expected_effect_template": "Turvallinen siviiliilmatilan hallinta UAV-tapahtuman aikana {infra}:n lähellä",
            "objective_template": "Vähentää siviiliilmatilan häiriöitä ja parantaa turvallisuutta vaikutusalueella.",
            "rationale_template": "Valittu, koska UAV-toiminta siviiliilmatilan lähellä vaatii koordinoitua siviili-turvallisuusjohtamista."
        },
        "sv": {
            "title_template": "Koordinera svar på civil luftrumssäkerhet",
            "description_template": "Rekommenderar samordning med civil luftfartsmyndighet för att hantera luftrummet runt det drabbade området. Stöd etablering av tillfälliga flygförbud. Dela tillgänglig sensordata med lufttrafikledning.",
            "assumptions": [
                "Civil luftfartsmyndighet är responsiv",
                "UAV eskalerar inte till intrång i kontrollerat luftrum",
                "Kommersiella omdirigeringar kan hanteras utan större störningar"
            ],
            "expected_effect_template": "Säker hantering av civil luftrum under UAV-incident nära {infra}",
            "objective_template": "Minska störningar i civil luftrum och förbättra säkerheten runt det drabbade området.",
            "rationale_template": "Vald eftersom UAV-aktivitet nära civil luftrum kräver koordinerad civil-säkerhetsledning."
        },
        "sq": {
            "title_template": "Koordinoni Përgjigjen e Sigurisë të Hapësirës Ajrore Civile",
            "description_template": "Rekomandojmë koordinim me autoritetin e aviacionit civil për të menaxhuar hapësirën ajrore rreth zonës së prekur. Mbështetja e vendosjes së kufizimeve të përkohshme të fluturimit. Ndani të dhënat e sensorëve të disponueshme me kontrollin e trafikut ajror.",
            "assumptions": [
                "Autoriteti i aviacionit civil është i përgjigjshëm",
                "UAV nuk eskalon në shkelje të hapësirës ajrore të kontrolluar",
                "Devijimet komerciale mund të menaxhohen pa ndërprerje të madhe"
            ],
            "expected_effect_template": "Menaxhim i sigurt i hapësirës ajrore civile gjatë incidentit të UAV pranë {infra}",
            "objective_template": "Reduktimi i ndërprerjes së hapësirës ajrore civile dhe përmirësimi i sigurisë rreth zonës së prekur.",
            "rationale_template": "Zgjedhur sepse aktiviteti i UAV pranë hapësirës ajrore civile kërkon menaxhim të koordinuar të sigurisë civile."
        },
        "mk": {
            "title_template": "Координирање на одговор за безбедност на цивилното воздушна простор",
            "description_template": "Препорачуваме координација со цивилното воздухопловно надлежно тело за управување со воздушниот простор околу погодената област. Поддршка за воспоставување временски забрани за лет. Споделете ги достапните сензорски податоци со контролата на воздухопловниот сообраќај.",
            "assumptions": [
                "Цивилното воздухопловно надлежно тело е реактивно",
                "UAV не ескалира до пробив на контролираниот воздушен простор",
                "Комерцијалните пренасочувања можат да се управуваат без големо нарушување"
            ],
            "expected_effect_template": "Безбедно управување со цивилниот воздушен простор за време на инцидент на UAV покрај {infra}",
            "objective_template": "Намалување на нарушувањето на цивилниот воздушен простор и подобрување на безбедноста околу погодената област.",
            "rationale_template": "Избрано бидејќи активност на UAV покрај цивилен воздушен простор бара координирано цивилно-безбедно управување."
        },
        "me": {
            "title_template": "Koordinacija Odgovora za Bezbednost Civilnog Vazduha",
            "description_template": "Preporučuje se koordinacija sa civilnom avijacionom autoritetom za upravljanje vazdušnim prostorom oko zahvaćenog područja. Podržati uspostavljanje privremenih ograničenja leta. Podeliti dostupne senzorske podatke sa kontrolom vazduhoplovstva.",
            "assumptions": [
                "Civilna avijaciona autoritet je reaktivan",
                "UAV ne eskalira do kršenja kontrolisanog vazdušnog prostora",
                "Komercijalne devijacije mogu biti upravljane bez velikog poremećaja"
            ],
            "expected_effect_template": "Sigurno upravljanje civilnim vazdušnim prostorom tokom incidenta UAV u blizini {infra}",
            "objective_template": "Smanjiti poremećaj civilnog vazdušnog prostora i poboljšati bezbednost oko zahvaćenog područja.",
            "rationale_template": "Odabrano jer aktivnosti UAV u blizini civilnog vazdušnog prostora zahtevaju koordinisano upravljanje civilnom bezbednošću."
        },
        "el": {
            "title_template": "Συντονισμός Αντιμετώπισης Ασφαλείας Αεροδιαστημικού Χώρου των Πολιτών",
            "description_template": "Συνιστάται η συντονισμός με την αρχή πολιτικής αεροπορίας για τη διαχείριση του αεροδιαστημικού χώρου γύρω από την επηρεαζόμενη περιοχή. Υποστήριξη στην ίδρυση προσωρινών περιορισμών πτήσης. Κοινή χρήση των διαθέσιμων δεδομένων αισθητήρων με τον ελεγκτή εναεικής κυκλοφορίας.",
            "assumptions": [
                "Η αρχή πολιτικής αεροπορίας είναι ανταποκρινόμενη",
                "Το UAV δεν κλιμακώνεται σε παραβίαση του ελεγχόμενου αεροδιαστημικού χώρου",
                "Οι εμπορικές αποκλίσεις μπορούν να διαχειριστούν χωρίς μεγάλη διακοπή"
            ],
            "expected_effect_template": "Ασφαλής διαχείριση πολιτικού αεροδιαστημικού χώρου κατά τη διάρκεια περιστατικού UAV κοντά στο {infra}",
            "objective_template": "Μείωση της διακοπής του πολιτικού αεροδιαστημικού χώρου και βελτίωση της ασφάλειας γύρω από την επηρεαζόμενη περιοχή.",
            "rationale_template": "Επιλέχθηκε επειδή η δραστηριότητα του UAV κοντά στον πολιτικό αεροδιαστημικό χώρο απαιτεί συντονισμένη διαχείριση πολιτικής ασφάλειας."
        }
    },
    "COA-TPL-BORDER": {
        "en": {
            "title_template": "Increase Border Monitoring and Information Sharing",
            "description_template": "Recommend increased monitoring of border areas where convoy activity has been reported. Coordinate information sharing with border security and allied intelligence. Maintain an awareness-focused posture.",
            "assumptions": [
                "Convoy activity is observable through existing ISR",
                "Border security forces can increase patrol frequency",
                "Convoy movements remain indicators requiring corroboration"
            ],
            "expected_effect_template": "Enhanced situational awareness of ground movements near {infra}",
            "objective_template": "Increase awareness of convoy activity and related movements near {infra}.",
            "rationale_template": "Selected because convoy indicators require cross-agency monitoring rather than isolated reporting."
        },
        "es": {
            "title_template": "Aumentar vigilancia fronteriza e intercambio de información",
            "description_template": "Se recomienda aumentar la vigilancia en zonas fronterizas donde se ha informado actividad de convoyes. Coordinar el intercambio de información con seguridad fronteriza e inteligencia aliada. Mantener una postura centrada en el conocimiento de situación.",
            "assumptions": [
                "La actividad de convoyes es observable mediante ISR existente",
                "Las fuerzas de seguridad fronteriza pueden aumentar la frecuencia de patrulla",
                "Los movimientos de convoy siguen siendo indicadores que requieren corroboración"
            ],
            "expected_effect_template": "Mayor conocimiento situacional de movimientos terrestres cerca de {infra}",
            "objective_template": "Aumentar el conocimiento de la actividad de convoyes y movimientos relacionados cerca de {infra}.",
            "rationale_template": "Se selecciona porque los indicadores de convoy requieren vigilancia interagencia y no informes aislados."
        },
        "fr": {
            "title_template": "Augmenter la Surveillance Frontalière et le Partage d'Informations",
            "description_template": "Recommander une surveillance accrue des zones frontalières où des activités de convoi ont été signalées. Coordonner le partage d'informations avec la sécurité frontalière et les renseignements alliés. Maintenir une posture axée sur la sensibilisation.",
            "assumptions": [
                "L'activité des convois est observable via l'ISR existant",
                "Les forces de sécurité frontalière peuvent augmenter la fréquence des patrouilles",
                "Les mouvements de convois restent des indicateurs nécessitant une corroboration"
            ],
            "expected_effect_template": "Sensibilisation accrue des mouvements terrestres près de {infra}",
            "objective_template": "Augmenter la sensibilisation à l'activité des convois et aux mouvements connexes près de {infra}.",
            "rationale_template": "Sélectionné car les indicateurs de convois nécessitent une surveillance inter-agences plutôt qu'un rapport isolé."
        },
        "de": {
            "title_template": "Grenzbewachung und Informationsaustausch erhöhen",
            "description_template": "Empfiehlt eine verstärkte Überwachung der Grenzgebiete, in denen Konvoibewegungen gemeldet wurden. Koordiniert den Informationsaustausch mit der Grenzsicherheit und alliierter Aufklärung. Aufrechterhaltung einer wachsamen Haltung.",
            "assumptions": [
                "Die Konvoibewegungen sind über bestehende ISR beobachtbar",
                "Die Grenzsicherheitskräfte können die Patrouillenfrequenz erhöhen",
                "Die Konvoibewegungen bleiben Indikatoren, die eine Bestätigung erfordern"
            ],
            "expected_effect_template": "Verbesserte Lagebewusstheit über Bodenbewegungen in der Nähe von {infra}",
            "objective_template": "Erhöhung der Wahrnehmung von Konvoibewegungen und damit verbundenen Bewegungen in der Nähe von {infra}.",
            "rationale_template": "Ausgewählt, da Konvoibewegungsindikatoren eine abteilungsübergreifende Überwachung und keine isolierte Meldung erfordern."
        },
        "it": {
            "title_template": "Aumentare il Monitoraggio del Confine e la Condivisione di Informazioni",
            "description_template": "Si raccomanda di aumentare il monitoraggio delle aree di confine dove sono state segnalate attività di convogli. Coordinare la condivisione di informazioni con la sicurezza del confine e le intelligence alleate. Mantenere una postura focalizzata sulla consapevolezza.",
            "assumptions": [
                "L'attività dei convogli è osservabile tramite ISR esistente",
                "Le forze di sicurezza del confine possono aumentare la frequenza delle pattuglie",
                "I movimenti dei convogli rimangono indicatori che richiedono corroborazione"
            ],
            "expected_effect_template": "Migliorata consapevolezza situazionale dei movimenti terrestri vicino a {infra}",
            "objective_template": "Aumentare la consapevolezza dell'attività dei convogli e dei movimenti correlati vicino a {infra}.",
            "rationale_template": "Selezionato perché gli indicatori di convoglio richiedono un monitoraggio inter-agenzia piuttosto che una segnalazione isolata."
        },
        "pt": {
            "title_template": "Aumentar o Monitoramento de Fronteira e Compartilhamento de Informações",
            "description_template": "Recomenda-se aumentar o monitoramento das áreas de fronteira onde foram relatadas atividades de comboio. Coordenar o compartilhamento de informações com a segurança de fronteira e inteligência aliada. Manter uma postura focada na consciência situacional.",
            "assumptions": [
                "A atividade do comboio é observável através de ISR existente",
                "As forças de segurança de fronteira podem aumentar a frequência de patrulha",
                "Os movimentos do comboio permanecem indicadores que requerem corroboração"
            ],
            "expected_effect_template": "Consciência situacional aprimorada de movimentos terrestres perto de {infra}",
            "objective_template": "Aumentar a consciência da atividade do comboio e movimentos relacionados perto de {infra}.",
            "rationale_template": "Selecionado porque os indicadores de comboio requerem monitoramento interinstitucional em vez de relatórios isolados."
        },
        "nl": {
            "title_template": "Verhoog Grensmonitoring en Informatiedeling",
            "description_template": "Aanbeveling tot verhoogde monitoring van grensgebieden waar konvooiactiviteit is gerapporteerd. Coördineren van informatie-uitwisseling met grensbeveiliging en geallieerde inlichtingendiensten. Handhaven van een bewustzijnsgerichte houding.",
            "assumptions": [
                "Konvooiactiviteit is observeerbaar via bestaande ISR",
                "Grensbeveiligingskrachten kunnen de patrouiliefrequentie verhogen",
                "Konvooimovementen blijven indicatoren die corroboratie vereisen"
            ],
            "expected_effect_template": "Verbeterde situationele bewustwording van grondbewegingen nabij {infra}",
            "objective_template": "Verhogen van het bewustzijn van konvooiactiviteit en gerelateerde bewegingen nabij {infra}.",
            "rationale_template": "Gekozen omdat konvooianalogen cross-agency monitoring vereisen in plaats van geïsoleerde rapportage."
        },
        "pl": {
            "title_template": "Zwiększenie Monitorowania Granicy i Udostępniania Informacji",
            "description_template": "Rekomenduje się zwiększone monitorowanie obszarów granicznych, gdzie zgłoszono aktywność konwojów. Koordynacja udostępniania informacji z bezpieczeństwem granicy i wywiadem sojuszniczym. Utrzymywanie postawy skoncentrowanej na świadomości.",
            "assumptions": [
                "Aktywność konwojów jest obserwowalna za pomocą istniejącego ISR",
                "Siły bezpieczeństwa granicznego mogą zwiększyć częstotliwość patroli",
                "Ruchy konwojów pozostają wskaźnikami wymagającymi potwierdzenia"
            ],
            "expected_effect_template": "Ulepszona świadomość sytuacyjna ruchów naziemnych w pobliżu {infra}",
            "objective_template": "Zwiększenie świadomości aktywności konwojów i powiązanych ruchów w pobliżu {infra}.",
            "rationale_template": "Wybrano, ponieważ wskaźniki konwojów wymagają monitorowania międzyagencji, a nie izolowanego raportowania."
        },
        "tr": {
            "title_template": "Sınır İzlemesini ve Bilgi Paylaşımını Artırın",
            "description_template": "Konvoy faaliyetlerinin bildirildiği sınır bölgelerinde izlemenin artırılmasını tavsiye eder. Sınır güvenliği ve müttefik istihbarat ile bilgi paylaşımını koordine edin. Farkındalık odaklı bir duruşu sürdürün.",
            "assumptions": [
                "Konvoy faaliyeti mevcut ISR aracılığıyla gözlemlenebilir",
                "Sınır güvenlik güçleri devriye sıklığını artırabilir",
                "Konvoy hareketleri doğrulama gerektiren göstergeler olarak kalır"
            ],
            "expected_effect_template": "{infra} yakınındaki kara hareketlerinin geliştirilmiş durum farkındalığı",
            "objective_template": "{infra} yakınındaki konvoy faaliyetleri ve ilgili hareketler hakkında farkındalığı artırmak.",
            "rationale_template": "Seçildi çünkü konvoy göstergeleri, izole raporlama yerine çapraz ajans izleme gerektirir."
        },
        "cs": {
            "title_template": "Zvýšit monitorování hranic a sdílení informací",
            "description_template": "Doporučuje se zvýšit monitorování oblastí hranic, kde byla hlášena činnost konvojů. Koordinovat sdílení informací s bezpečnostními silami na hranicích a spojeneckou inteligencí. Udržovat postavu zaměřenou na povědomí.",
            "assumptions": [
                "Činnost konvojů je pozorovatelná prostřednictvím stávajícího ISR",
                "Silám na hranicích lze zvýšit frekvenci patroly",
                "Pohyby konvojů zůstávají indikátory vyžadující ověření"
            ],
            "expected_effect_template": "Zlepšené situční povědomí o наземných pohybech poblíž {infra}",
            "objective_template": "Zvýšit povědomí o činnosti konvojů a souvisejících pohybech poblíž {infra}.",
            "rationale_template": "Vybráno, protože indikátory konvojů vyžadují monitorování napříč agenturami, nikoli izolované hlášení."
        },
        "ro": {
            "title_template": "Creșterea Monitorizării Frontierelor și a Schimbului de Informații",
            "description_template": "Se recomandă creșterea monitorizării zonelor frontaliere unde au fost raportate activități de convoai. Coordonați schimbul de informații cu securitatea frontierelor și informațiile aliate. Mențineți o postură axată pe conștiință.",
            "assumptions": [
                "Activitatea convoaielor este observabilă prin ISR existent",
                "Forțele de securitate a frontierelor pot crește frecvența patrulării",
                "Mișcările convoaielor rămân indicatori care necesită corroborare"
            ],
            "expected_effect_template": "Conștiință situațională îmbunătățită a mișcărilor terestre în apropierea {infra}",
            "objective_template": "Creșterea conștiinței privind activitatea convoaielor și mișcările asociate în apropierea {infra}.",
            "rationale_template": "Selectat deoarece indicatorii convoaielor necesită monitorizare interagenții în loc de raportare izolata."
        },
        "hu": {
            "title_template": "Növelni a Határ Megfigyelését és Az Információ Megosztását",
            "description_template": "Ajánlott növelni a határ területeken történő megfigyelést, ahol konvoj tevékenységről számoltak be. Koordinálni az információmegosztást a határbiztonsággal és a szövetséges intelligenciával. Fenntartani egy tudatosságra fókuszáló pozíciót.",
            "assumptions": [
                "A konvoj tevékenysége látható az aktuális ISR-en keresztül",
                "A határbiztonsági erők növelhetik a patroll gyakoriságát",
                "A konvoj mozgásai olyan indikátorok maradnak, amelyek megerősítést igényelnek"
            ],
            "expected_effect_template": "Mezőmozgások fokozott helyzetinformációja a {infra} közelében",
            "objective_template": "Növelni a konvoj tevékenységének és kapcsolódó mozgásoknak a {infra} közelében való tudatosságát.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a konvoj indikátorok átkereső ügynökségi monitorozást igényel, nem pedig elszigetelt jelentést."
        },
        "bg": {
            "title_template": "Увеличаване на Граничното Наблюдение и Споделяне на Информация",
            "description_template": "Препоръчва се увеличено наблюдение на граничните зони, където са докладвани дейности на конвои. Координирайте споделянето на информация с граничната охрана и съюзническата разузнавателна информация. Поддържайте позиция, фокусирана върху осведомеността.",
            "assumptions": [
                "Дейностите на конвоя са наблюдаеми чрез съществуващи ISR",
                "Силите за гранична охрана могат да увеличат честотата на патрулиране",
                "Движенията на конвоя остават индикатори, изискващи потвърждение"
            ],
            "expected_effect_template": "Подобрена ситуационна осведоменост за наземните движения близо до {infra}",
            "objective_template": "Увеличаване на осведомеността за дейностите на конвоя и свързаните движения близо до {infra}.",
            "rationale_template": "Избрано, защото индикаторите на конвоя изискват мониторинг между агенциите, а не изолирано докладване."
        },
        "hr": {
            "title_template": "Povećanje Nadzora Granice i Dijeljenje Informacija",
            "description_template": "Preporučuje se povećan nadzor granica gdje su prijavljene aktivnosti konvoja. Koordinirati dijeljenje informacija s graničnom sigurnošću i saveznom obavještajnom službom. Održavati stav fokusiran na svijest.",
            "assumptions": [
                "Aktivnosti konvoja su vidljive putem postojećeg ISR-a",
                "Granična sigurnosna snaga može povećati učestalost patrola",
                "Pokreti konvoja ostaju indikatori koji zahtijevaju potvrdu"
            ],
            "expected_effect_template": "Poboljšana situacijska svijest o pomacima na kopnu u blizini {infra}",
            "objective_template": "Povećati svijest o aktivnostima konvoja i srodnim pomacima u blizini {infra}.",
            "rationale_template": "Odabrano jer indikatori konvoja zahtijevaju nadzor više agencija umjesto izoliranog izvještavanja."
        },
        "sk": {
            "title_template": "Zvýšiť monitorovanie hraníc a zdieľanie informácií",
            "description_template": "Odporúča sa zvýšené monitorovanie hranícových oblastí, kde bola hlásená činnosť konvojov. Koordinovať zdieľanie informácií s hranícnou bezpečnosťou a spojeneckou inteligenciou. Udržať postoj zameraný na povedomie.",
            "assumptions": [
                "Činnosť konvojov je pozorovatelná prostredníctvom existujúceho ISR",
                "Hranícne bezpečnostné zriadenia môžu zvýšiť frekvenciu patroly",
                "Hmovy konvojov zostávajú ukazovateľmi vyžadujúcimi potvrdenie"
            ],
            "expected_effect_template": "Zlepšené situčné povedomie o наземných pohyboch blízko {infra}",
            "objective_template": "Zvýšiť povedomie o činnosti konvojov a súvisiacich pohyboch blízko {infra}.",
            "rationale_template": "Vybrané, pretože ukazovatele konvojov vyžadujú monitorovanie naprieč agentúrami namiesto izolovaného hlásenia."
        },
        "sl": {
            "title_template": "Povečanje nadzora na meji in deljenje informacij",
            "description_template": "Priporoča se povečano nadzorovanje območij meje, kjer so poročeni dejavnosti konvojjev. Koordinirajte deljenje informacij z varnostjo meje in zavezniško inteligenco. Ohranite držo osredotočenosti na obvestitev.",
            "assumptions": [
                "Dejavnosti konvojjev so opazljive skozi obstoječi ISR",
                "Sile za varnost meje lahko povečajo frekvenco patrole",
                "Migracije konvojjev ostajajo indikatorji, ki zahtevajo potrditev"
            ],
            "expected_effect_template": "Izboljšana situacijska obvestitev o zemljiških gibanjih blizu {infra}",
            "objective_template": "Povečanje obvestitve o dejavnostih konvojjev in povezanih gibanjih blizu {infra}.",
            "rationale_template": "Izbrano, ker indikatorji konvojjev zahtevajo nadzor med agencijami, namesto izoliranega poročanja."
        },
        "et": {
            "title_template": "Täpsustada piirivalvatus ja teabe jagamine",
            "description_template": "Soovitatakse piirialade valvamise suurendamist, kus on raportitud konvooaktiivsuse kohta. Koordineerige teabe jagamist piirivalvatus- ja liitaste teadmistega. Püsige teadlikkuse keskendunud seisukohas.",
            "assumptions": [
                "Konvooaktiivsus on nähtav olemasoleva ISR kaudu",
                "Piirivalvatusväe saavad valvamise sagedust suurendada",
                "Konvoo liikumised jäävad näitajaeks, millele on vaja kinnitamist"
            ],
            "expected_effect_template": "Parandatud olukorda teadlikkus maa liikumiste kohta {infra} läheduses",
            "objective_template": "Täpsustada teadlikkus konvooaktiivsuse ja seotud liikumiste kohta {infra} läheduses.",
            "rationale_template": "Valitud, sest konvoo näitajad nõuavad läbivõetavat agentuuride jälgimist, mitte eraldatud raportimist."
        },
        "lv": {
            "title_template": "Palielināt robežas uzraudzību un informācijas apmaiņu",
            "description_template": "Ieteicams palielināt robežas teritoriju uzraudzību, kur ir ziņots par konvoju aktivitāti. Koordinēt informācijas apmaiņu ar robežas drošības un alliēšu izlūkošanu. Saglabāt uzmetumu, kas ir fokusēts uz zināšanu.",
            "assumptions": [
                "Konvoju aktivitāte ir skatāma caur esošo ISR",
                "Robežas drošības spēki var palielināt patrulhošanas biežumu",
                "Konvoju kustības paliek indikatori, kas prasa apstiprināšanu"
            ],
            "expected_effect_template": "Uzlabota situācijas zināšana par zemes kustībām tuvumā {infra}",
            "objective_template": "Palielināt zināšanu par konvoju aktivitāti un saistītām kustībām tuvumā {infra}.",
            "rationale_template": "Izvēlēts, jo konvoju indikatori prasa starpinstitucijālu uzraudzību, nevis izolētu ziņošanu."
        },
        "lt": {
            "title_template": "Padidinti Gabinimo Stebėjimą ir Informacijos Dalinimo",
            "description_template": "Regaliam padidinti stebėjimą per sienos teritorijas, kur buvo pranešta konvojų veikla. Koordinuoti informacijos dalinimą su sienos saugumo ir alysių buhnto inteligencija. Išlaikyti fokusuojantį įsitikimą.",
            "assumptions": [
                "Konvojų veikla yra pastebima per esamą ISR",
                "Sienos saugumo pajėgos gali padidinti patrolybos dažnumą",
                "Konvojų judėjimas išlieka rodikliais, reikalaujančiais patvirtinimo"
            ],
            "expected_effect_template": "Gerinintas situacijos supratimas apie žemės judėjimą prie {infra}",
            "objective_template": "Padidinti supratimą apie konvojų veikla ir susijusius judėjimus prie {infra}.",
            "rationale_template": "Pasirinkta, nes konvojų rodikliai reikalauja tarpagentūrinių stebėjimo, o ne izoliuoto pranešimo."
        },
        "da": {
            "title_template": "Øg Grænseovervågning og Informationsdeling",
            "description_template": "Anbefaler øget overvågning af grænseområder, hvor konvojaktivitet er blevet rapporteret. Koordiner informationsdeling med grænse-sikkerhed og allieret efterretning. Oprethold en bevidsthedsfokuseret holdning.",
            "assumptions": [
                "Konvojaktivitet er observerbar gennem eksisterende ISR",
                "Grænse-sikkerhedsstyrker kan øge patruljefrekvensen",
                "Konvojbevægelser forbliver indikatorer, der kræver bekræftelse"
            ],
            "expected_effect_template": "Forbedret situationsfornemmelse af jordbevægelser nær {infra}",
            "objective_template": "Øg bevidstheden om konvojaktivitet og relaterede bevægelser nær {infra}.",
            "rationale_template": "Valgt, fordi konvojindikatorer kræver tværgående agenturovervågning frem for isoleret rapportering."
        },
        "no": {
            "title_template": "Øke grenseovervåking og informasjonsdeling",
            "description_template": "Anbefaler økt overvåking av grenseområder der konvoiaktivitet er rapportert. Koordinere informasjonsdeling med grensesikkerhet og alliert etterretning. Opprettholde en bevissthetsfokusert holdning.",
            "assumptions": [
                "Konvoiaktivitet er observerbar gjennom eksisterende ISR",
                "Grensesikkerhetsstyrker kan øke patruljefrekvensen",
                "Konvoimomentene forblir indikatorer som krever korroborering"
            ],
            "expected_effect_template": "Forbedret situasjonsforståelse av bakkeforflytninger nær {infra}",
            "objective_template": "Øke bevisstheten om konvoiaktivitet og relaterte bevegelser nær {infra}.",
            "rationale_template": "Valgt fordi konvoindikatorer krever tverrsektor overvåking fremfor isolert rapportering."
        },
        "is": {
            "title_template": "Auka eftirlit á landbrigðum og deila upplýsingum",
            "description_template": "Mætir með aukinni eftirlit á landbrigðsvæðum þar sem konvoi virkni hefur verið skýrð. Samræmd upplýsingadeild með landbrigðsvarnir og samstarfandi underrannsóknir. Halda varkárni-fokustu stöðu.",
            "assumptions": [
                "Konvoi virkni er sjáanleg með til staðandi ISR",
                "Landbrigðsvarnir geta aukið eftirlitsfrekvens",
                "Konvoi hreyfingar halda fram á merkjum sem krefjast staðfestingar"
            ],
            "expected_effect_template": "Auka stöðugleika á sjávarhreyfingum nær {infra}",
            "objective_template": "Auka varkárni á konvoi virkni og tengdum hreyfingum nær {infra}.",
            "rationale_template": "Valinn því að konvoi merki krefjast samstarfandi eftirlits í stað þess að skila áinsættum skýrslum."
        },
        "fi": {
            "title_template": "Lisää rajavalvontaa ja tiedonjakelua",
            "description_template": "Suositellaan rajavyöhykkeen valvontaa lisäämistä alueilla, joilla konvoitoimintaa on raportoitu. Koordinoi tiedonjakelu rajatarkkailun ja liittoutuneen tiedustelun kanssa. Ylläpidä tietoisuuteen keskittyvää asentoa.",
            "assumptions": [
                "Konvoitoiminta on havaittavissa olemassa olevan ISR:n kautta",
                "Rajatarkkailujoukot voivat lisätä partiointitiheyttä",
                "Konvoonliikkeet pysyvät indikaattoreina, jotka vaativat vahvistusta"
            ],
            "expected_effect_template": "Parantunut tilannetietoisuus maaliikenteestä {infra}:n lähellä",
            "objective_template": "Lisää tietoisuutta konvoitoiminnasta ja siihen liittyvistä liikkeistä {infra}:n lähellä.",
            "rationale_template": "Valittu, koska konvoonindikaattorit vaativat eri toimijoiden valvontaa eikä erillistä raportointia."
        },
        "sv": {
            "title_template": "Öka gränsövervakning och informationsdelning",
            "description_template": "Rekommenderar ökad övervakning av gränsområden där konvojaktivitet har rapporterats. Koordinera informationsdelning med gränssäkerhet och allierad underrättelse. Bibehåll en medvetenhetsfokuserad hållning.",
            "assumptions": [
                "Konvojaktivitet är observerbar genom befintlig ISR",
                "Gränssäkerhetsstyrkor kan öka patrullfrekvensen",
                "Konvojrörelser förblir indikatorer som kräver bekräftelse"
            ],
            "expected_effect_template": "Förbättrad situationsmedvetenhet om markrörelser nära {infra}",
            "objective_template": "Öka medvetenheten om konvojaktivitet och relaterade rörelser nära {infra}.",
            "rationale_template": "Vald eftersom konvojindikatorer kräver tvärsektoriell övervakning snarare än isolerad rapportering."
        },
        "sq": {
            "title_template": "Rritni Monitorimin e Kufirit dhe Ndarjen e Informacionit",
            "description_template": "Rekomandojmë rritjen e monitorimit të zonave kufitare ku janë raportuar aktivitetet e konvojeve. Koordinoni ndarjen e informacionit me sigurinë e kufirit dhe inteligjencën e aleatëve. Mbani një qëndrim të fokusuar në ndërgjegjësim.",
            "assumptions": [
                "Aktiviteti i konvojeve është i vëzhgueshëm përmes ISR ekzistues",
                "Forcat e sigurisë kufitare mund të rrisin frekuencën e patrullimit",
                "Lëvizjet e konvojeve mbeten tregues që kërkojnë korborim"
            ],
            "expected_effect_template": "Ndërgjegjësim i përmirësuar i lëvizjeve të tokës pranë {infra}",
            "objective_template": "Rritja e ndërgjegjësimit për aktivitetin e konvojeve dhe lëvizjet e lidhura pranë {infra}.",
            "rationale_template": "Zgjedhur sepse treguesit e konvojeve kërkojnë monitorim ndër-agjencial në vend të raportimit të izoluar."
        },
        "mk": {
            "title_template": "Зголемување на следењето на границата и споделување на информации",
            "description_template": "Препорачуваме зголено следење на границите каде што се известуваат активности на конвој. Координирајте споделување на информации со граничната безбедност и сојузната интелегенција. Одржувајте позиција фокусирана на свесност.",
            "assumptions": [
                "Активностите на конвојот се забележливи преку постоечки ISR",
                "Силите за гранична безбедност можат да го зголемат честотата на патрулирање",
                "Движењата на конвојот остануваат индикатори кои бараат потврда"
            ],
            "expected_effect_template": "Подобрена ситуационална свесност за земјните движења покрај {infra}",
            "objective_template": "Зголемување на свесноста за активностите на конвојот и поврзаните движења покрај {infra}.",
            "rationale_template": "Избрано бидејќи индикаторите на конвојот бараат надзор преку агенциите наместо изолирано известување."
        },
        "me": {
            "title_template": "Povećanje Nadzora Granice i Deljenja Informacija",
            "description_template": "Preporučuje se povećan nadzor granica gde su prijavljene aktivnosti konvoja. Koordinirati deljenje informacija sa graničnom bezbednošću i saveznom obaveštajnom službom. Održavati stav fokusiran na svest.",
            "assumptions": [
                "Aktivnosti konvoja su vidljive kroz postojeći ISR",
                "Granične snage mogu povećati frekvenciju patrola",
                "Pokreti konvoja ostaju indikatori koji zahtevaju potvrdu"
            ],
            "expected_effect_template": "Poboljšana situaciona svest o kopnenim pokretima u blizini {infra}",
            "objective_template": "Povećati svest o aktivnostima konvoja i srodnim pokretima u blizini {infra}.",
            "rationale_template": "Odabrano jer indikatori konvoja zahtevaju nadzor više agencija, a ne samo izolirano izveštavanje."
        },
        "el": {
            "title_template": "Αύξηση της Παρακολούθησης των Συνοδίων και της Ανταλλαγής Πληροφοριών",
            "description_template": "Συνιστάται αυξημένη παρακολούθηση των περιοχών των συνόρων όπου αναφέρθηκε δραστηριότητα काफिलेα. Συντονισμός της ανταλλαγής πληροφοριών με την ασφάλεια των συνόρων και την συμμαχική αν развед. Διατήρηση στάσης εστιασμένης στην ενημέρωση.",
            "assumptions": [
                "Η δραστηριότητα του काफिलेα είναι παρατηρήσιμη μέσω των υφιστάμενων ISR",
                "Οι δυνάμεις ασφαλείας των συνόρων μπορούν να αυξήσουν τη συχνότητα των περιπολιών",
                "Οι κινήσεις του काफिलेα παραμένουν δείκτες που απαιτούν επιβεβαίωση"
            ],
            "expected_effect_template": "Βελτιωμένη ситуационная ενημέρωση για τις κινήσεις στο πεδίο κοντά στο {infra}",
            "objective_template": "Αύξηση της ενημέρωσης για τη δραστηριότητα του काफिलेα και τις σχετικές κινήσεις κοντά στο {infra}.",
            "rationale_template": "Επιλέχθηκε επειδή οι δείκτες του काफिलेα απαιτούν παρακολούθηση από διάφορες υπηρεσίες αντί για απομονωμένη αναφορά."
        }
    },
    "COA-TPL-COMBINED": {
        "en": {
            "title_template": "Combined Observation, Cable Protection, and Border Monitoring",
            "description_template": "Recommend a combined approach: shadow {entities} while simultaneously increasing observation of {infra} and expanding border monitoring. Most resource-intensive but addresses all threat vectors.",
            "assumptions": [
                "Sufficient assets available for multi-axis response",
                "Coordination staff can manage concurrent advisory workflows",
                "Logistics support is available for extended operations"
            ],
            "expected_effect_template": "Comprehensive coverage across all threat domains near {infra}",
            "objective_template": "Coordinate observation, protection, and contingency posture around {infra} and {entities}.",
            "rationale_template": "Selected because multiple concurrent threat indicators justify a combined, resource-intensive response posture."
        },
        "es": {
            "title_template": "Observación combinada, protección de cable y vigilancia fronteriza",
            "description_template": "Se recomienda un enfoque combinado: hacer sombra a {entities} mientras se incrementa simultáneamente la observación de {infra} y se amplía la vigilancia fronteriza. Es la opción más intensiva en recursos, pero cubre todos los vectores de amenaza.",
            "assumptions": [
                "Hay medios suficientes para una respuesta en varios ejes",
                "El personal de coordinación puede gestionar flujos consultivos concurrentes",
                "Existe apoyo logístico para operaciones prolongadas"
            ],
            "expected_effect_template": "Cobertura integral en todos los dominios de amenaza cerca de {infra}",
            "objective_template": "Coordinar observación, protección y postura de contingencia alrededor de {infra} y {entities}.",
            "rationale_template": "Se selecciona porque múltiples indicadores simultáneos de amenaza justifican una postura combinada e intensiva en recursos."
        },
        "fr": {
            "title_template": "Observation Combinée, Protection des Câbles et Surveillance Frontalière",
            "description_template": "Recommander une approche combinée : suivre les {entities} tout en augmentant simultanément l'observation de {infra} et en élargissant la surveillance frontalière. Le plus gourmand en ressources, mais il aborde tous les vecteurs de menace.",
            "assumptions": [
                "Des actifs suffisants sont disponibles pour une réponse multi-axes",
                "Le personnel de coordination peut gérer les flux de travail consultatifs simultanés",
                "Le soutien logistique est disponible pour des opérations prolongées"
            ],
            "expected_effect_template": "Couverture complète sur tous les domaines de menace près de {infra}",
            "objective_template": "Coordonner l'observation, la protection et la posture de contingence autour de {infra} et des {entities}.",
            "rationale_template": "Sélectionné car de multiples indicateurs de menace simultanés justifient une posture de réponse combinée et intensive en ressources."
        },
        "de": {
            "title_template": "Kombinierte Beobachtung, Kabelschutz und Grenzbewachung",
            "description_template": "Empfiehlt einen kombinierten Ansatz: {entities} beobachten, während gleichzeitig die Beobachtung von {infra} erhöht und die Grenzbewachung erweitert wird. Ressourcenintensivste, adressiert aber alle Bedrohungsvektoren.",
            "assumptions": [
                "Ausreichende Assets für eine mehrachsige Reaktion verfügbar",
                "Koordinationspersonal kann gleichzeitige Beratungsworkflows verwalten",
                "Logistikunterstützung ist für erweiterte Operationen verfügbar"
            ],
            "expected_effect_template": "Umfassende Abdeckung über alle Bedrohungsdomänen in der Nähe von {infra}",
            "objective_template": "Koordination von Beobachtung, Schutz und Kontingenzhaltung rund um {infra} und {entities}.",
            "rationale_template": "Ausgewählt, da mehrere gleichzeitige Bedrohungsindikatoren eine kombinierte, ressourcenintensive Reaktionshaltung rechtfertigen."
        },
        "it": {
            "title_template": "Osservazione Combinata, Protezione del Cavo e Monitoraggio del Confine",
            "description_template": "Si raccomanda un approccio combinato: sorvegliare {entities} mentre si aumenta contemporaneamente l'osservazione di {infra} ed si espande il monitoraggio del confine. Più intensivo in termini di risorse, ma affronta tutti i vettori di minaccia.",
            "assumptions": [
                "Asset sufficienti disponibili per una risposta multi-asse",
                "Lo staff di coordinamento può gestire flussi di lavoro di avviso concorrenti",
                "Il supporto logistico è disponibile per operazioni prolungate"
            ],
            "expected_effect_template": "Copertura completa in tutti i domini di minaccia vicino a {infra}",
            "objective_template": "Coordinare osservazione, protezione e postura di emergenza intorno a {infra} e {entities}.",
            "rationale_template": "Selezionato perché più indicatori di minaccia concorrenti giustificano una postura di risposta combinata e intensiva in termini di risorse."
        },
        "pt": {
            "title_template": "Observação Combinada, Proteção de Cabo e Monitoramento de Fronteira",
            "description_template": "Recomenda-se uma abordagem combinada: acompanhar {entities} enquanto simultaneamente aumenta a observação de {infra} e expande o monitoramento de fronteira. Mais intensivo em recursos, mas aborda todos os vetores de ameaça.",
            "assumptions": [
                "Ativos suficientes disponíveis para resposta multi-eixo",
                "A equipe de coordenação pode gerenciar fluxos de trabalho de aconselhamento concorrentes",
                "Suporte logístico disponível para operações estendidas"
            ],
            "expected_effect_template": "Cobertura abrangente em todos os domínios de ameaça perto de {infra}",
            "objective_template": "Coordenar observação, proteção e postura de contingência ao redor de {infra} e {entities}.",
            "rationale_template": "Selecionado porque múltiplos indicadores de ameaça concorrentes justificam uma postura de resposta combinada e intensiva em recursos."
        },
        "nl": {
            "title_template": "Gecombineerde Observatie, Kabelbescherming en Grensmonitoring",
            "description_template": "Aanbeveling voor een gecombineerde aanpak: schaduw {entities} terwijl tegelijkertijd de observatie van {infra} wordt verhoogd en de grensmonitoring wordt uitgebreid. Meest resource-intensief, maar adresseert alle dreigingsvectoren.",
            "assumptions": [
                "Voldoende middelen beschikbaar voor multi-as respons",
                "Coördinatieteams kunnen gelijktijdige adviesworkflows beheren",
                "Logistieke ondersteuning is beschikbaar voor uitgebreide operaties"
            ],
            "expected_effect_template": "Omvattende dekking over alle dreigingsdomeinen nabij {infra}",
            "objective_template": "Coördineren van observatie, bescherming en contingente houding rond {infra} en {entities}.",
            "rationale_template": "Gekozen omdat meerdere gelijktijdige dreigingsindicatoren een gecombineerde, resource-intensieve respons houding rechtvaardigen."
        },
        "pl": {
            "title_template": "Połączona Obserwacja, Ochrona Kabli i Monitorowanie Granicy",
            "description_template": "Rekomenduje się podejście połączone: śledzenie {entities} przy jednoczesnym zwiększeniu obserwacji {infra} i rozszerzeniu monitorowania granicy. Najbardziej zasobożerne, ale adresuje wszystkie wektory zagrożenia.",
            "assumptions": [
                "Dostępne wystarczające zasoby do reakcji wieloosiowej",
                "Personel koordynacyjny może zarządzać równoczesnymi przepływami doradczymi",
                "Wsparcie logistyczne jest dostępne dla wydłużonych operacji"
            ],
            "expected_effect_template": "Kompleksowe pokrycie wszystkich domen zagrożeń w pobliżu {infra}",
            "objective_template": "Koordynacja obserwacji, ochrony i postawy awaryjnej wokół {infra} i {entities}.",
            "rationale_template": "Wybrano, ponieważ wiele równoczesnych wskaźników zagrożenia uzasadnia połączoną, zasobożerną postawę reakcji."
        },
        "tr": {
            "title_template": "Birleşik Gözlem, Kablo Koruma ve Sınır İzleme",
            "description_template": "Birleşik bir yaklaşım tavsiye eder: {entities}'yı gölgeleme ile eş zamanlı olarak {infra}'nın gözlemini artırma ve sınır izlemesini genişletme. En çok kaynak tüketen ancak tüm tehdit vektörlerini ele alan yaklaşım.",
            "assumptions": [
                "Çok eksenli yanıt için yeterli varlık mevcut",
                "Koordinasyon personeli eş zamanlı danışmanlık iş akışlarını yönetebilir",
                "Genişletilmiş operasyonlar için lojistik destek mevcut"
            ],
            "expected_effect_template": "{infra} yakınındaki tüm tehdit alanlarında kapsamlı kapsama",
            "objective_template": "{infra} ve {entities} çevresinde gözlem, koruma ve acil durum duruşunu koordine etmek.",
            "rationale_template": "Seçildi çünkü birden fazla eş zamanlı tehdit göstergesi, birleşik, kaynak yoğun bir yanıt duruşunu haklı çıkarmaktadır."
        },
        "cs": {
            "title_template": "Kombinované pozorování, ochrana kabelů a monitorování hranic",
            "description_template": "Doporučuje se kombinovaný přístup: sledovat {entities} a zároveň zvyšovat pozorování {infra} a rozšiřovat monitorování hranic. Nejnáročnější z hlediska zdrojů, ale řeší všechny vektory hrozby.",
            "assumptions": [
                "Dostatek prostředků k reakci na více os",
                "Personál pro koordinaci dokáže zvládnout současné pracovní postupy",
                "Logistická podpora je k dispozici pro prodloužené operace"
            ],
            "expected_effect_template": "Komplexní pokrytí všech domén hrozby poblíž {infra}",
            "objective_template": "Koordinovat pozorování, ochranu a postavu na případ nouze kolem {infra} a {entities}.",
            "rationale_template": "Vybráno, protože více současných indikátorů hrozby ospravedlňuje kombinovanou postavu reakce s vysokou náročností na zdroje."
        },
        "ro": {
            "title_template": "Observare Combinată, Protecție a Cablului și Monitorizare a Frontierelor",
            "description_template": "Se recomandă o abordare combinată: umbrarea {entities} în timp ce se crește simultan observația {infra} și se extinde monitorizarea frontierelor. Cel mai intens din punct de vedere al resurselor, dar abordează toate vectorii de amenințare.",
            "assumptions": [
                "Resurse suficiente disponibile pentru răspuns multi-axial",
                "Personalul de coordonare poate gestiona fluxurile de sfaturi concurente",
                "Suportul logistic este disponibil pentru operațiuni extinse"
            ],
            "expected_effect_template": "Acoperire cuprinzătoare în toate domeniile de amenințare în apropierea {infra}",
            "objective_template": "Coordonarea observației, protecției și posturii de contingeniu în jurul {infra} și {entities}.",
            "rationale_template": "Selectat deoarece multiple indicatori de amenințare concurenți justifică o postură de răspuns combinat, intens din punct de vedere al resurselor."
        },
        "hu": {
            "title_template": "Kombinált Megfigyelés, Kábelvédelem és Határ Megfigyelés",
            "description_template": "Ajánlott kombinált megközelítés: árnyékolni a {entities}-t, miközben egyben növelni a {infra} megfigyelését és bővíteni a határ megfigyelését. Legtöbb erőforrást igénylő, de minden fenyegetési vektorot lefedi.",
            "assumptions": [
                "Elég sok eszköz rendelkezésre áll több tengelyes válaszhoz",
                "A koordinációs személyzet kezelheti a párhuzamos tanácsadási munkafolyamatokat",
                "A logisztikai támogatás elérhető hosszabb műveletekhez"
            ],
            "expected_effect_template": "Teljes fedezettség minden fenyegetési területen a {infra} közelében",
            "objective_template": "Koordinálni a megfigyelést, védelmet és sürgősségi pozíciót a {infra} és {entities} körül.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert több párhuzamos fenyegetési indikátor jogosít egy kombinált, erőforrás-igényes válasz pozíciót."
        },
        "bg": {
            "title_template": "Комбинирано Наблюдение, Защита на Кабела и Гранично Мониторинг",
            "description_template": "Препоръчва се комбиниран подход: следване на {entities}, като същевременно се увеличава наблюдението на {infra} и се разширява граничният мониторинг. Най-интензивен от гледна точка на ресурсите, но адресира всички вектори на заплаха.",
            "assumptions": [
                "Достатъци активи са налични за многоосвен отговор",
                "Персоналът за координация може да управлява едновременни работни потоци на съвети",
                "Логистичната подкрепа е налична за продължителни операции"
            ],
            "expected_effect_template": "Изчерпателно покритие във всички домейни на заплаха близо до {infra}",
            "objective_template": "Координация на наблюдение, защита и контингентна позиция около {infra} и {entities}.",
            "rationale_template": "Избрано, защото множество едновременни индикатори на заплаха оправдават комбинирана, ресурсоемка позиция на отговор."
        },
        "hr": {
            "title_template": "Kombinirani Nadzor, Zaštita Kabela i Nadzor Granice",
            "description_template": "Preporučuje se kombinirani pristup: praćenje {entities} dok istovremeno povećavate nadzor {infra} i proširujete nadzor granice. Najviše resursno intenzivan, ali adresira sve vektore prijetnje.",
            "assumptions": [
                "Dostupno je dovoljno sredstava za višasmjerni odgovor",
                "Struka za koordinaciju može upravljati istovremenim radnim tokovima savjetovanja",
                "Logistička podrška je dostupna za produžene operacije"
            ],
            "expected_effect_template": "Sveobuhvatna pokrivenost u svim domenama prijetnje u blizini {infra}",
            "objective_template": "Koordinirati nadzor, zaštitu i kontingentni stav oko {infra} i {entities}.",
            "rationale_template": "Odabrano jer više istovremenih indikatora prijetnje opravdava kombinirani, resursno intenzivan stav odgovora."
        },
        "sk": {
            "title_template": "Spojené sledovanie, ochrana kábla a monitorovanie hraníc",
            "description_template": "Odporúča sa kombinovaný prístup: sledovať {entities} zatiaľ čo zároveň zvyšovať sledovanie {infra} a rozširovať monitorovanie hraníc. Najviac náročné na zdroje, ale rieši všetky vektory hrozby.",
            "assumptions": [
                "Dostatočné aktíva sú dostupné pre viacosmernú reakciu",
                "Koordinátorstvo môže riadiť súběžné pracovné toky poradenstva",
                "Logistická podpora je dostupná pre rozšírené operácie"
            ],
            "expected_effect_template": "Komplexné pokrytie všetkých domén hrozby blízko {infra}",
            "objective_template": "Koordinovať sledovanie, ochranu a postoj na prípad na {infra} a {entities}.",
            "rationale_template": "Vybrané, pretože viacero súběžných ukazovateľov hrozby ospravedlňuje kombinovaný postoj reakcie s vysokou náročnosťou na zdroje."
        },
        "sl": {
            "title_template": "Združeno opažanje, zaščita kabla in nadzor meje",
            "description_template": "Priporoča se kombiniran pristop: sledenje {entities} hkrati z povečanjem opažanja {infra} in širjenjem nadzora na meji. Največ resursno zahteven, vendar obravnava vse vektorje amebe.",
            "assumptions": [
                "Dostopno je dovolj sredstev za večosmeren odziv",
                "Osebje za koordinacijo lahko upravlja sorčajne potoke obvestitev",
                "Logistična podpora je na voljo za podaljšane operacije"
            ],
            "expected_effect_template": "Vseobhodno pokrivanje v vseh domenah amebe blizu {infra}",
            "objective_template": "Koordinirati opažanje, zaščito in stanje pripravljenosti za izjeme okoli {infra} in {entities}.",
            "rationale_template": "Izbrano, ker več indikatorjev amebe zahteva kombiniran, resursno zahteven pristop odziva."
        },
        "et": {
            "title_template": "Kombineeritud jälgimine, kaabli kaitse ja piirivalvatus",
            "description_template": "Soovitatakse kombineeritud lähenemist: varjendaada {entities}, samal ajal suurendada {infra} jälgimist ja laiendada piirivalvatus. Kõige ressursivaimne, kuid vastab kõigile ohtlikute vektoritele.",
            "assumptions": [
                "Piisav varad on saadaval mitmeakssele vastusele",
                "Koordineerimispersonaal saab samal ajal nõuande töövoogude hallata",
                "Logistika toetus on saadaval pikemate operatsioonide jaoks"
            ],
            "expected_effect_template": "Komprehensiivne katte kõigil ohtlikute valdkondades {infra} läheduses",
            "objective_template": "Koordineerida jälgimist, kaitset ja reaktiivset seisukohta {infra} ja {entities} ümber.",
            "rationale_template": "Valitud, sest mitmed samal ajal ohtlikud näitajad õigustavad kombineeritud, ressursivaimset vastuse seisukohta."
        },
        "lv": {
            "title_template": "Kombinēta observācija, kabela aizsardzība un robežas uzraudzība",
            "description_template": "Ieteicams kombinēts pieeja: atsekt {entities}, vienlaikus palielinot {infra} observāciju un paplašinot robežas uzraudzību. Visbiežāk resursintensīvs, bet risina visus draudens vektorus.",
            "assumptions": [
                "Pieejami pietiekami resursi multi-akses reakcijai",
                "Koordinācijas darbinieki var vadīt vienlaikus padomus (advisory) darba procesus",
                "Logistikas atbalsts ir pieejams ilgstošām operācijām"
            ],
            "expected_effect_template": "Vissvarīga apkalpošana visās draudens sfērās tuvumā {infra}",
            "objective_template": "Koordinēt observāciju, aizsardzību un ārkārtas pozīciju apriet {infra} un {entities}.",
            "rationale_template": "Izvēlēts, jo vairāki vienlaici draudens indikatori pamato kombinētu, resursintensīvu reakcijas pozīciju."
        },
        "lt": {
            "title_template": "Sąjungtas Stebėjimas, Kabelio Apsauga ir Sienos Stebėjimas",
            "description_template": "Regaliam sąjunginį požiūrį: sekti {entities}, registruodami {infra} stebėjimą ir išplėsdami sienos stebėjimą. Labiausiai išteklių intensyvus, bet apima visus grėsmės vektorius.",
            "assumptions": [
                "Yra pakankamai išteklių daugiašveičio atsakymui",
                "Koordinavimo darbuotojai gali valdyti vienu metu esančiomis patarimų srautais",
                "Logistikos palaikymas yra prieinamas ilgalaikiams operacijoms"
            ],
            "expected_effect_template": "Visapusiškas pokrovimas visose grėsmės srityse prie {infra}",
            "objective_template": "Koordinuoti stebėjimą, apsaugą ir avarijos būseną aplink {infra} ir {entities}.",
            "rationale_template": "Pasirinkta, nes daugybė vienu metu esančių grėsmės rodiklių pagrįsta sąjunginį, išteklių intensyvų atsakymo būseną."
        },
        "da": {
            "title_template": "Kombineret Observation, Kabelbeskyttelse og Grænseovervågning",
            "description_template": "Anbefaler en kombineret tilgang: skygge {entities} samtidig med at man øger observationen af {infra} og udvider grænseovervågningen. Mest ressourcekrævende, men adresserer alle trusselsvektorer.",
            "assumptions": [
                "Tilstrækkelige aktiver til multi-akse respons er tilgængelige",
                "Koordinationspersonale kan håndtere samtidige rådgivningsworkflows",
                "Logistikstøtte er tilgængelig for udvidede operationer"
            ],
            "expected_effect_template": "Omfattende dækning på tværs af alle trusselsdomæner nær {infra}",
            "objective_template": "Koordiner observation, beskyttelse og beredskab omkring {infra} og {entities}.",
            "rationale_template": "Valgt, fordi flere samtidige trusselsindikatorer retfærdiggør en kombineret, ressourcekrævende responsstilling."
        },
        "no": {
            "title_template": "Kombinert observasjon, kabelbeskyttelse og grenseovervåking",
            "description_template": "Anbefaler en kombinert tilnærming: skygge {entities} samtidig som man øker observasjonen av {infra} og utvider grenseovervåkingen. Mest ressurskrevende, men adresserer alle trusselvektorer.",
            "assumptions": [
                "Tilstrekkelige ressurser tilgjengelig for flerakse respons",
                "Koordineringspersonell kan håndtere samtidige rådgivningsarbeidsflyter",
                "Logistisk støtte er tilgjengelig for utvidede operasjoner"
            ],
            "expected_effect_template": "Omfattende dekning på tvers av alle trusseldomener nær {infra}",
            "objective_template": "Koordinere observasjon, beskyttelse og beredskapsstilling rundt {infra} og {entities}.",
            "rationale_template": "Valgt fordi flere samtidige trusselindikatorer rettferdiggjør en kombinert, ressurskrevende responsstilling."
        },
        "is": {
            "title_template": "Samþætt eftirlit, vernd kebla og eftirlit á landbrigðum",
            "description_template": "Mætir með samþættum nálgun: skugga {entities} meðan samstundis aukast eftirlit á {infra} og fjárnætur landbrigðs eftirlit. Mest auðlindar-þungt en það takar ábyrgð á öllum hættulegum vettvangum.",
            "assumptions": [
                "Tæknilegar auðlindir til málflokkuðrar ábyrgðar eru til staðar",
                "Samræmingarstarfsmenn geta stjórnað samstundandi ráðgjafastöðum",
                "Logistíska stuðningur er til staðar fyrir lengri aðgerðir"
            ],
            "expected_effect_template": "Allhvernlega þekking yfir öll hættulega svæði nær {infra}",
            "objective_template": "Samræma eftirlit, vernd og óvænt stöðu um {infra} og {entities}.",
            "rationale_template": "Valinn því að fleir samstundandi hættulegir merki leyfa samþættan, auðlindar-þunga ábyrgðar stöðu."
        },
        "fi": {
            "title_template": "Yhdistetty havainnointi, kaapelisuojaus ja rajavalvonta",
            "description_template": "Suositellaan yhdistettyä lähestymistapaa: seuraa {entities}:ä samalla kun lisätään havainnointia {infra}:n alueella ja laajennetaan rajavalvontaa. Resurssi-intensiivisin, mutta käsittelee kaikki uhka-alueet.",
            "assumptions": [
                "Riittävästi varusteita saatavilla moniaksiseen vastaukseen",
                "Koordinaatiop henkilöstö voi hallita samanaikaisia neuvontaprosesseja",
                "Logistiikkatuenti on saatavilla laajennettuihin operaatioihin"
            ],
            "expected_effect_template": "Kattava kattavuus kaikilla uhka-alueilla {infra}:n lähellä",
            "objective_template": "Koordinoi havainnointi, suojaus ja varautumisasento {infra}:n ja {entities}:n ympärillä.",
            "rationale_template": "Valittu, koska useat samanaikaiset uhkaindikaattorit oikeuttavat yhdistetyn, resurssi-intensiivisen vastauksen asennon."
        },
        "sv": {
            "title_template": "Kombinerad observation, kabelskydd och gränsövervakning",
            "description_template": "Rekommenderar en kombinerad strategi: skugga {entities} samtidigt som observationen av {infra} ökas och gränsövervakningen utökas. Mest resurskrävande men adresserar alla hotvektorer.",
            "assumptions": [
                "Tillräckliga tillgångar tillgängliga för respons på flera axlar",
                "Koordinationspersonal kan hantera samtidiga rådgivningsarbetsflöden",
                "Logistikstöd är tillgängligt för utökade operationer"
            ],
            "expected_effect_template": "Omfattande täckning över alla hotdomäner nära {infra}",
            "objective_template": "Koordinera observation, skydd och beredskapsställning kring {infra} och {entities}.",
            "rationale_template": "Vald eftersom flera samtidiga hotindikatorer motiverar en kombinerad, resurskrävande responsställning."
        },
        "sq": {
            "title_template": "Vëzhgim i Bashkuar, Mbrojtje e Kabllos dhe Monitorim i Kufirit",
            "description_template": "Rekomandojmë një qasje të kombinuar: hajroni {entities} ndërkohë që rritni njëkohësisht vëzhgimin e {infra} dhe zgjeroni monitorimin e kufirit. Më intensiv në burime, por adreson të gjitha vektorët e kërcënimit.",
            "assumptions": [
                "Asetet e mjaftueshme janë të disponueshme për përgjigje shumë-aksiale",
                "Stafi i koordinimit mund të menaxhojë rrjedhët e këshillimit të përbashkëta",
                "Mbështetja logjistike është e disponueshme për operacione të zgjatura"
            ],
            "expected_effect_template": "Mbulim i plotë në të gjitha fushat e kërcënimit pranë {infra}",
            "objective_template": "Koordinoni vëzhgimin, mbrojtjen dhe qëndrimin e kontingjencës rreth {infra} dhe {entities}.",
            "rationale_template": "Zgjedhur sepse treguesit e shumtë të kërcënimit të përbashkët justifikojnë një qëndrim përgjigjës të kombinuar, intensiv në burime."
        },
        "mk": {
            "title_template": "Комбинирано следење, заштита на кабелот и следење на границата",
            "description_template": "Препорачуваме комбиниран пристап: следење на {entities} додека истовремено зголемуваме следење на {infra} и го прошируваме следењето на границата. Најинтензивен по ресурси, но адресира сите вектори на закана.",
            "assumptions": [
                "Достапни активи за мултиаксивен одговор",
                "Персоналијата за координација може да управува со паралелни работни процеси на советување",
                "Логистичката поддршка е достапна за продолжени операции"
            ],
            "expected_effect_template": "Комплетно покривање низ сите домени на заканата покрај {infra}",
            "objective_template": "Координирање на следење, заштита и позиција за контингенција околу {infra} и {entities}.",
            "rationale_template": "Избрано бидејќи повеќе паралелни индикатори на закана оправдуваат комбинирана позиција на одговор со висока потрошувачка на ресурси."
        },
        "me": {
            "title_template": "Kombinovani Nadzor, Zaštita Kabla i Nadzor Granice",
            "description_template": "Preporučuje se kombinovani pristup: praćenje {entities} dok se istovremeno povećava nadzor {infra} i proširuje nadzor granice. Najzahtevniji po resursima, ali adresira sve vektore pretnji.",
            "assumptions": [
                "Dovoljno sredstava dostupno za višasmeran odgovor",
                "Staf za koordinaciju može upravljati istovremenim radovima savetovanja",
                "Logistička podrška je dostupna za produžene operacije"
            ],
            "expected_effect_template": "Sveobuhvatna pokrivenost u svim domenima pretnji u blizini {infra}",
            "objective_template": "Koordinirati nadzor, zaštitu i kontingentni stav oko {infra} i {entities}.",
            "rationale_template": "Odabrano jer više istovremenih indikatora pretnji opravdava kombinovani, intenzivan odgovor."
        },
        "el": {
            "title_template": "Συνδυασμένη Παρακολούθηση, Προστασία Καλωδίου και Παρακολούθηση Συνόρων",
            "description_template": "Συνιστάται μια συνδυασμένη προσέγγιση: σκίαση των {entities} ενώ ταυτόχρονα αυξάνεται η παρατήρηση του {infra} και επεκτείνεται η παρακολούθηση των συνόρων. Το πιο απαιτητικό σε πόρους, αλλά αντιμετωπίζει όλες τις κατευθύνσεις απειλής.",
            "assumptions": [
                "Διαθέσιμα επαρκή περιουσιακά στοιχεία για πολυάξο σε απάντηση",
                "Το προσωπικό συντονισμού μπορεί να διαχειριστεί ταυτόχρονες ροές συμβουλών",
                "Η υποστήριξη της εφοδιαστικής αλυσίδας είναι διαθέσιμη για εκτεταμένες επιχειρήσεις"
            ],
            "expected_effect_template": "Ολοκληρωμένη κάλυψη σε όλες τις ζώνες απειλής κοντά στο {infra}",
            "objective_template": "Συντονισμός παρατήρησης, προστασίας και στάσης έκτακτης ανάγκης γύρω από το {infra} και τα {entities}.",
            "rationale_template": "Επιλέχθηκε επειδή πολλαπλοί ταυτόχρονες δείκτες απειλής δικαιολογούν μια συνδυασμένη στάση απάντησης, απαιτητική σε πόρους."
        }
    },
    "COA-TPL-REINFORCE": {
        "en": {
            "title_template": "Request Additional Allied Support and Sustain Monitoring",
            "description_template": "Current contact pressure exceeds the immediately available friendly support posture. Recommend requesting additional allied maritime and ISR coverage while sustaining monitoring of {entities} and the {infra} area.",
            "assumptions": [
                "Higher headquarters or partners can allocate additional support",
                "Existing local forces can maintain observation until relief arrives",
                "The operating picture remains fluid and requires coordinated reinforcement"
            ],
            "expected_effect_template": "Improved friendly force balance and monitoring resilience around {infra}",
            "objective_template": "Stabilize the surveillance posture and request reinforcements for {entities} near {infra}.",
            "rationale_template": "Selected because contact pressure currently exceeds the friendly support available in theater."
        },
        "es": {
            "title_template": "Solicitar apoyo aliado adicional y sostener la vigilancia",
            "description_template": "La presión actual de contactos supera la postura de apoyo amigo disponible de inmediato. Se recomienda solicitar cobertura marítima aliada e ISR adicional mientras se mantiene la vigilancia sobre {entities} y la zona de {infra}.",
            "assumptions": [
                "El escalón superior o socios pueden asignar apoyo adicional",
                "Las fuerzas locales actuales pueden mantener la observación hasta el relevo",
                "La situación operativa sigue siendo fluida y requiere refuerzo coordinado"
            ],
            "expected_effect_template": "Mejor equilibrio de fuerzas amigas y resiliencia de vigilancia alrededor de {infra}",
            "objective_template": "Estabilizar la postura de vigilancia y solicitar refuerzos para {entities} cerca de {infra}.",
            "rationale_template": "Se selecciona porque la presión de contactos supera actualmente el apoyo amigo disponible en teatro."
        },
        "fr": {
            "title_template": "Demander un Soutien Allié Supplémentaire et Maintenir la Surveillance",
            "description_template": "La pression de contact actuelle dépasse la posture de soutien amical immédiatement disponible. Recommander de demander une couverture maritime et ISR alliée supplémentaire tout en maintenant la surveillance des {entities} et de la zone {infra}.",
            "assumptions": [
                "Le haut commandement ou les partenaires peuvent allouer un soutien supplémentaire",
                "Les forces locales existantes peuvent maintenir l'observation jusqu'à l'arrivée des renforts",
                "Le tableau opérationnel reste fluide et nécessite un renforcement coordonné"
            ],
            "expected_effect_template": "Amélioration de l'équilibre des forces amies et de la résilience de la surveillance autour de {infra}",
            "objective_template": "Stabiliser la posture de surveillance et demander des renforts pour les {entities} près de {infra}.",
            "rationale_template": "Sélectionné car la pression de contact dépasse actuellement le soutien amical disponible dans le théâtre."
        },
        "de": {
            "title_template": "Zusätzliche alliierte Unterstützung anfordern und Überwachung aufrechterhalten",
            "description_template": "Der aktuelle Kontaktdruck übersteigt die unmittelbar verfügbare freundliche Unterstützungshaltung. Empfiehlt die Anforderung zusätzlicher alliierter maritimer und ISR-Abdeckung bei gleichzeitiger Aufrechterhaltung der Überwachung von {entities} und dem {infra}-Gebiet.",
            "assumptions": [
                "Höhere Kommandoebenen oder Partner können zusätzliche Unterstützung bereitstellen",
                "Die bestehenden lokalen Kräfte können die Beobachtung aufrechterhalten, bis Hilfe eintrifft",
                "Das Lagebild bleibt fließend und erfordert koordinierte Verstärkung"
            ],
            "expected_effect_template": "Verbesserte Balance der freundlichen Kräfte und Überwachungsresilienz rund um {infra}",
            "objective_template": "Stabilisierung der Überwachungshaltung und Anforderung von Verstärkungen für {entities} in der Nähe von {infra}.",
            "rationale_template": "Ausgewählt, da der Kontaktdruck derzeit die verfügbare freundliche Unterstützung im Einsatzgebiet übersteigt."
        },
        "it": {
            "title_template": "Richiedere Supporto Alleato Aggiuntivo e Mantenere il Monitoraggio",
            "description_template": "La pressione di contatto attuale supera la postura di supporto amichevole immediatamente disponibile. Si raccomanda di richiedere copertura marittima e ISR alleata aggiuntiva mantenendo il monitoraggio di {entities} e dell'area {infra}.",
            "assumptions": [
                "Il quartier generale superiore o i partner possono allocare supporto aggiuntivo",
                "Le forze locali esistenti possono mantenere l'osservazione fino all'arrivo del soccorso",
                "Il quadro operativo rimane fluido e richiede un rafforzamento coordinato"
            ],
            "expected_effect_template": "Miglioramento dell'equilibrio delle forze amiche e della resilienza del monitoraggio intorno a {infra}",
            "objective_template": "Stabilizzare la postura di sorveglianza e richiedere rinforzi per {entities} vicino a {infra}.",
            "rationale_template": "Selezionato perché la pressione di contatto supera attualmente il supporto amichevole disponibile nel teatro."
        },
        "pt": {
            "title_template": "Solicitar Apoio Aliado Adicional e Sustentar Monitoramento",
            "description_template": "A pressão de contato atual excede a postura de apoio amigável imediatamente disponível. Recomenda-se solicitar cobertura marítima e de ISR aliada adicional enquanto se sustenta o monitoramento de {entities} e da área {infra}.",
            "assumptions": [
                "O alto comando ou parceiros podem alocar apoio adicional",
                "As forças locais existentes podem manter a observação até a chegada do reforço",
                "O quadro operacional permanece fluido e requer reforço coordenado"
            ],
            "expected_effect_template": "Melhor equilíbrio das forças amigas e resiliência do monitoramento ao redor de {infra}",
            "objective_template": "Estabilizar a postura de vigilância e solicitar reforços para {entities} perto de {infra}.",
            "rationale_template": "Selecionado porque a pressão de contato atualmente excede o apoio amigável disponível no teatro."
        },
        "nl": {
            "title_template": "Verzoek om Aanvullende Geallieerde Ondersteuning en Onderhoud van Monitoring",
            "description_template": "Huidige contactdruk overtreft de onmiddellijk beschikbare vriendschappelijke ondersteuningshouding. Aanbeveling om aanvullende geallieerde maritieme en ISR-dekking aan te vragen terwijl de monitoring van {entities} en het {infra} gebied wordt volgehouden.",
            "assumptions": [
                "Hoofdkwartier of partners kunnen aanvullende ondersteuning toewijzen",
                "Bestaande lokale troepen kunnen observatie handhaven totdat verlichting arriveert",
                "Het operationele beeld blijft vloeiend en vereist gecoördineerde versterking"
            ],
            "expected_effect_template": "Verbeterde vriendschappelijke krachtbalans en monitoring veerkracht rond {infra}",
            "objective_template": "Stabiliseren van de surveillancehouding en versterkingen aanvragen voor {entities} nabij {infra}.",
            "rationale_template": "Gekozen omdat de contactdruk momenteel de beschikbare vriendschappelijke ondersteuning in het theater overtreft."
        },
        "pl": {
            "title_template": "Żądanie Dodatkowego Sojuszniczego Wsparcia i Utrzymanie Monitorowania",
            "description_template": "Obecny nacisk kontaktowy przekracza natychmiastową postawę wsparcia sojuszniczego. Rekomenduje się żądanie dodatkowego sojuszniczego pokrycia morskiego i ISR przy jednoczesnym utrzymaniu monitorowania {entities} i obszaru {infra}.",
            "assumptions": [
                "Wyższe dowództwo lub partnerzy mogą przydzielić dodatkowe wsparcie",
                "Istniejące siły lokalne mogą utrzymywać obserwację do czasu nadejścia pomocy",
                "Obraz operacyjny pozostaje płynny i wymaga skoordynowanego wzmocnienia"
            ],
            "expected_effect_template": "Poprawa równowagi sił sojuszniczych i odporności monitorowania wokół {infra}",
            "objective_template": "Stabilizacja postawy nadzoru i żądanie wzmocnień dla {entities} w pobliżu {infra}.",
            "rationale_template": "Wybrano, ponieważ nacisk kontaktowy obecnie przekracza dostępne wsparcie sojusznicze w teatrze działań."
        },
        "tr": {
            "title_template": "Ek Müttefik Desteği Talep Edin ve İzlemeyi Sürdürün",
            "description_template": "Mevcut temas baskısı, derhal mevcut dost destek duruşunu aşmaktadır. {entities} ve {infra} alanının izlenmesini sürdürürken ek müttefik deniz ve ISR kapsamı talep etmeyi tavsiye eder.",
            "assumptions": [
                "Üst komuta veya ortaklar ek destek tahsis edebilir",
                "Mevcut yerel kuvvetler rahatlama gelene kadar gözlemi sürdürebilir",
                "Operasyonel resim akışkan kalmaya devam ediyor ve koordineli takviye gerektiriyor"
            ],
            "expected_effect_template": "{infra} çevresinde dost kuvvet dengesinin ve izleme dayanıklılığının iyileşmesi",
            "objective_template": "{infra} yakınındaki {entities} için gözetleme duruşunu stabilize etmek ve takviye talep etmek.",
            "rationale_template": "Seçildi çünkü temas baskısı şu anda sahadaki dost desteği aşmaktadır."
        },
        "cs": {
            "title_template": "Žádat o dodatečnou spojeneckou podporu a udržovat monitorování",
            "description_template": "Aktuální tlak kontaktu přesahuje okamžitě dostupnou postavu přátelské podpory. Doporučuje se požádat o dodatečné spojenecké maritimní a ISR pokrytí při udržování monitorování {entities} a oblasti {infra}.",
            "assumptions": [
                "Vyšší velení nebo partneři mohou přidělit dodatečnou podporu",
                "Stávající místní síly mohou udržet pozorování do příjezdu pomoci",
                "Operační obraz zůstává dynamický a vyžaduje koordinované posílení"
            ],
            "expected_effect_template": "Zlepšená rovnováha přátelských sil a odolnost monitorování kolem {infra}",
            "objective_template": "Stabilizovat postavu dohledu a požádat o posílení pro {entities} poblíž {infra}.",
            "rationale_template": "Vybráno, protože tlak kontaktu v současné době přesahuje přátelskou podporu dostupnou v teatru."
        },
        "ro": {
            "title_template": "Solicitare de Suport Suplimentar Aliat și Susținerea Monitorizării",
            "description_template": "Presiunea curentă de contact depășește postura de suport prietenos imediat disponibil. Se recomandă solicitarea de acoperire maritimă și ISR suplimentară aliată, menținând în același timp monitorizarea {entities} și a zonei {infra}.",
            "assumptions": [
                "Statul major superior sau partenerii pot aloca suport suplimentar",
                "Forțele locale existente pot menține observația până când ajunge ajutorul",
                "Imaginea operațională rămâne fluidă și necesită întărire coordonată"
            ],
            "expected_effect_template": "Îmbunătățirea echilibrului forțelor prietene și reziliența monitorizării în jurul {infra}",
            "objective_template": "Stabilizarea posturii de supraveghere și solicitarea de întărire pentru {entities} în apropierea {infra}.",
            "rationale_template": "Selectat deoarece presiunea de contact depășește în prezent suportul prietenos disponibil în teatru."
        },
        "hu": {
            "title_template": "Kérelm További Szövetséges Támogatásért és Fenntartott Monitorozásért",
            "description_template": "Az aktuális kapcsolatnyomás meghaladja a közvetlenül elérhető baráti támogatási pozíciót. Ajánlott kérni további szövetséges tengeri és ISR fedezettséget, miközben fenntartjuk a {entities} és a {infra} terület monitorozását.",
            "assumptions": [
                "A felső vezetés vagy partnerek tudnak további támogatást rendelni",
                "Az aktuális erők fenntarthatják a megfigyelést, amíg a segély megérkezik",
                "A működési kép folytonos marad és koordinált megerősítést igényel"
            ],
            "expected_effect_template": "Jobb baráti erők egyensúly és monitorozási rugalmasság a {infra} körül",
            "objective_template": "Stabilizálni a felügyeleti pozíciót és kérni megerősítést a {entities} közelében a {infra}-hoz.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert a kapcsolatnyomás jelenleg meghaladja a helyszíni baráti támogatást."
        },
        "bg": {
            "title_template": "Искане за Допълнителна Съюзническа Подкрепа и Поддържане на Мониторинга",
            "description_template": "Текущото напрежение на контакта надхвърля незабавното налично съюзническо позициониране. Препоръчва се искане за допълнително съюзно морско и ISR покритие, като същевременно се поддържа мониторинг на {entities} и зоната {infra}.",
            "assumptions": [
                "Високите штабове или партньорите могат да разпределят допълнителна подкрепа",
                "Съществуващите местни сили могат да поддържат наблюдение до пристигането на облекчението",
                "Оперативната картина остава динамична и изисква координирано подсилване"
            ],
            "expected_effect_template": "Подобрен баланс на съюзните сили и устойчивост на мониторинга около {infra}",
            "objective_template": "Стабилизиране на позицията за наблюдение и искане на подсилване за {entities} близо до {infra}.",
            "rationale_template": "Избрано, защото напрежението на контакта в момента надхвърля съюзната подкрепа, налична в театра."
        },
        "hr": {
            "title_template": "Zahtjev za Dodatnu Saveznu Podršku i Održavanje Nadzora",
            "description_template": "Trenutni pritisak kontakta premašuje odmah dostupni stav prijateljske podrške. Preporučuje se zahtjev za dodatnu saveznu pomorsku i ISR pokrivenost uz održavanje nadzora {entities} i područja {infra}.",
            "assumptions": [
                "Vrhovni štab ili partneri mogu dodijeliti dodatnu podršku",
                "Postojeće lokalne snage mogu održati nadzor dok ne stigne olakšanje",
                "Operativna slika ostaje fluidna i zahtijeva koordinirano pojačanje"
            ],
            "expected_effect_template": "Poboljšana ravnoteža prijateljskih snaga i otpornost nadzora oko {infra}",
            "objective_template": "Stabilizirati stav nadzora i zatražiti pojačanje za {entities} u blizini {infra}.",
            "rationale_template": "Odabrano jer trenutni pritisak kontakta premašuje dostupnu prijateljsku podršku u teatru."
        },
        "sk": {
            "title_template": "Požiadať o dodatočnú spojeneckú podporu a udržiavať monitorovanie",
            "description_template": "Aktuálny tlak kontaktu prekračuje okamžite dostupný postoj priateľskej podpory. Odporúča sa požiadať o dodatočné spojenecké morské a ISR pokrytie pri udržiavaní monitorovania {entities} a oblasti {infra}.",
            "assumptions": [
                "Vyššie velenie alebo partneri môžu vyznačiť dodatočnú podporu",
                "Existujúce miestne síly môžu udržiavať sledovanie, kým dorazí pomoc",
                "Operačný obraz zostáva dynamický a vyžaduje koordinovanú posilnenie"
            ],
            "expected_effect_template": "Zlepšené vyváženie priateľských síl a odolnosť monitorovania okolo {infra}",
            "objective_template": "Stabilizovať postoj sledovania a požiadať o posilnenie pre {entities} blízko {infra}.",
            "rationale_template": "Vybrané, pretože tlak kontaktu momentálne prekračuje priateľskú podporu dostupnú v teatre."
        },
        "sl": {
            "title_template": "Zahtev za dodatno zavezniško podporo in vzdrževanje nadzora",
            "description_template": "Trenutni pritisk kontakta presega takoj dostopno zavezniško stanje podpore. Priporoča se zahtevanje dodatnega zavezniškega pomorskega in ISR pokrivanja, hkrati z vzdrževanjem nadzora nad {entities} in območjem {infra}.",
            "assumptions": [
                "Višji štab ali partnerji lahko dodelijo dodatno podporo",
                "Obstojne lokalne sile lahko vzdržijo opažanje do prihodnje pomoči",
                "Operativna slika ostaja dinamična in zahteva koordinirano umnoževanje"
            ],
            "expected_effect_template": "Izboljšano ravnovesje zavezniških sil in odpornost nadzora okoli {infra}",
            "objective_template": "Stabilizirati stanje nadzora in zahtevati umnoževanje za {entities} blizu {infra}.",
            "rationale_template": "Izbrano, ker trenutni pritisk kontakta presega zavezniško podporo, dostopno v teatru."
        },
        "et": {
            "title_template": "Paluge lisaliitaste toetust ja säilitage jälgimine",
            "description_template": "Praegune kontakti rõh ületab koheselt saadaval olevat liitaste toetuse seisukohta. Soovitatakse paluda lisaliitaste merelist ja ISR katet, samal ajal säilitades jälgimise {entities} ja {infra} ala kohta.",
            "assumptions": [
                "Keskjuhtkond või partnerid saavad lisatoetust allokate",
                "Olemasolevad kohalikud jõud saavad jälgimise säilitada, kuni abi saabub",
                "Operatsioonipilt jääb pidevalt muutuvaks ja nõuab koordineeritud täpsustamist"
            ],
            "expected_effect_template": "Parandatud liitaste jõudude tasakaal ja jälgimise vastupidavus {infra} ümber",
            "objective_template": "Stabiliseerida jälgimise seisukohta ja paluda täpsustamist {entities} läheduses {infra}.",
            "rationale_template": "Valitud, sest kontakti rõh ületab praegu tegevusala liitaste toetuse."
        },
        "lv": {
            "title_template": "Eiropas atbalsta pieprasījums un uzlabota uzraudzība",
            "description_template": "Padēse kontakta spiediens pārsniedz tūlītroši pieejamo draudzīgā atbalsta pozīciju. Ieteicams pieprasīt papildu alliēšu jūras un ISR apkalpošanu, saglabājot uzraudzību par {entities} un {infra} teritoriju.",
            "assumptions": [
                "Augstākā vadība vai partneri var alocēt papildu atbalstu",
                "Esošajām vietējām spējām var saglabāt observāciju, kamēr ierodas atbalsts",
                "Operācijas attēls paliek dinamisks un prasa koordinētu pastiprinājumu"
            ],
            "expected_effect_template": "Uzlabots draudzīgās spēku balanss un uzraudzības izturība tuvumā {infra}",
            "objective_template": "Stabilizēt uzraudzības pozīciju un pieprasīt pastiprinājumus par {entities} tuvumā {infra}.",
            "rationale_template": "Izvēlēts, jo kontakta spiediens pašlaik pārsniedz draudzīgās atbalsta pieejamību teātrā."
        },
        "lt": {
            "title_template": "Prašyti Papildomos Alysių Pagalbos ir Palaikyti Stebėjimo",
            "description_template": "Dabartinis kontakto spaudimas viršija iškart prieinamą draugiškų palaikymo būseną. Regaliam prašyti papildomos alysių jūrinės ir ISR pokrovimo, išlaikant stebėjimą {entities} ir {infra} teritorijoje.",
            "assumptions": [
                "Viršapijos komanda ar partneriai gali paskirstyti papildomą pagalbą",
                "Esami vietiniai pajėgos gali išlaikyti stebėjimą, kol atvyks palikimas",
                "Operavimo vaizdas išlieka dinamiškas ir reikalauja koordinuoto palaikymo"
            ],
            "expected_effect_template": "Gerinintas draugiškų pajėgų subalansuoti ir stebėjimo atsparumas aplink {infra}",
            "objective_template": "Stabilizuoti stebėjimo būseną ir prašyti pagalbos {entities} prie {infra}.",
            "rationale_template": "Pasirinkta, nes kontakto spaudimas šiuo metu viršija draugiškų palaikymo, esantio teatre."
        },
        "da": {
            "title_template": "Anmod om Yderligere Allieret Støtte og Oprethold Overvågning",
            "description_template": "Nuværende kontaktpres overstiger den umiddelbart tilgængelige venlige støtteposition. Anbefaler at anmode om yderligere allieret maritim og ISR dækning, samtidig med at overvågningen af {entities} og {infra} området opretholdes.",
            "assumptions": [
                "Højere kommando eller partnere kan tildele yderligere støtte",
                "Eksisterende lokale styrker kan opretholde observation, indtil lettelse ankommer",
                "Driftsbilledet forbliver flydende og kræver koordineret forstærkning"
            ],
            "expected_effect_template": "Forbedret venlig styrkebalance og overvågningsmodstandsdygtighed omkring {infra}",
            "objective_template": "Stabiliser overvågningspositionen og anmod om forstærkninger til {entities} nær {infra}.",
            "rationale_template": "Valgt, fordi kontaktpresset i øjeblikket overstiger den venlige støtte, der er tilgængelig i teateret."
        },
        "no": {
            "title_template": "Be om tilleggsstøtte fra allierte og oppretthold overvåking",
            "description_template": "Nåværende kontaktpress overstiger den umiddelbart tilgjengelige vennlige støtteposisjonen. Anbefaler å be om tilleggsalliert maritim og ISR-dekning samtidig som overvåkingen av {entities} og {infra}-området opprettholdes.",
            "assumptions": [
                "Høyere kommando eller partnere kan tildele tilleggsstøtte",
                "Eksisterende lokale styrker kan opprettholde observasjon til hjelpen ankommer",
                "Operasjonelt bilde forblir flytende og krever koordinert forsterkning"
            ],
            "expected_effect_template": "Forbedret balanse av vennlige styrker og overvåkingsmotstandskraft rundt {infra}",
            "objective_template": "Stabilisere overvåkingsstillingen og be om forsterkninger for {entities} nær {infra}.",
            "rationale_template": "Valgt fordi kontaktpresset for tiden overstiger den vennlige støtten som er tilgjengelig i teateret."
        },
        "is": {
            "title_template": "Beíða viðbótlegt samstarfandi stuðning og viðhalda eftirliti",
            "description_template": "Nýja sambandsþrýstingur yfirirskarar þá strax til staðandi vinna stuðningar stöðu. Mætir með að biðja um viðbótlegt samstarfandi sjó- og ISR-þekking meðan eftirlit yfir {entities} og {infra} svæðið haldist.",
            "assumptions": [
                "Hægri staðsetning eða samstarfsaðilar geta berað út viðbótlegt stuðning",
                "Til staðandi staðbundnar styrkur getur haldið eftirliti þar til aðstoð kemur",
                "Virkni myndarins heldur sig flæðandi og krefst samræmdar styrkingu"
            ],
            "expected_effect_template": "Bætt vinna styrk og eftirlitarþol um {infra}",
            "objective_template": "Staðleggja eftirlitarstöðu og biðja um styrkingu fyrir {entities} nær {infra}.",
            "rationale_template": "Valinn því að sambandsþrýstingur yfirirskarar þá vinna stuðning sem er til staðar í svæðinu."
        },
        "fi": {
            "title_template": "Pyydä lisäliittoutuneita tukivoimia ja ylläpidä seurantaa",
            "description_template": "Nykyinen kontaktipaine ylittää välittömästi saatavilla olevan liittolaisvastauksen. Suositellaan pyytämistä lisäliittoutuneita meri- ja ISR-kattoa samalla kun seuranta {entities}:n ja {infra}-alueen kohdalla ylläpidetään.",
            "assumptions": [
                "Päämaja tai kumppanit voivat allokoida lisätukea",
                "Olemassa olevat paikalliset joukot voivat ylläpitää havainnointia kunnes apu saapuu",
                "Toimintakuva pysyy dynaamisena ja vaatii koordinoitua vahvistusta"
            ],
            "expected_effect_template": "Parantunut liittolaisjoukkojen tasapaino ja seurannan kestävyys {infra}:n ympärillä",
            "objective_template": "Stabiloi valvontatila ja pyydä vahvistusta {entities}:n lähellä {infra}:a.",
            "rationale_template": "Valittu, koska kontaktipaine ylittää tällä hetkellä kentällä saatavilla olevan liittolaisvastauksen."
        },
        "sv": {
            "title_template": "Begär ytterligare allierat stöd och bibehåll övervakning",
            "description_template": "Nuvarande kontaktpress överstiger den omedelbart tillgängliga vänliga stödställningen. Rekommenderar att begära ytterligare allierad sjö- och ISR-täckning samtidigt som övervakningen av {entities} och {infra}-området upprätthålls.",
            "assumptions": [
                "Högre högkvarter eller partners kan tilldela ytterligare stöd",
                "Befintliga lokala styrkor kan bibehålla observation tills förstärkning anländer",
                "Operativbilden förblir flytande och kräver koordinerad förstärkning"
            ],
            "expected_effect_template": "Förbättrad balans av vänliga styrkor och övervakningsresiliens kring {infra}",
            "objective_template": "Stabilisera övervakningsställningen och begära förstärkningar för {entities} nära {infra}.",
            "rationale_template": "Vald eftersom kontaktpressen för närvarande överstiger det vänliga stödet som finns tillgängligt i teatern."
        },
        "sq": {
            "title_template": "Kërkoni Mbështetje Shtesë të Aleatëve dhe Mbani Monitorimin",
            "description_template": "Presioni i kontaktit aktual tejkalon qëndrimin e mbështetjes të disponueshme të forcave miqësore. Rekomandojmë kërkimin e mbulimit shtesë detar dhe ISR të aleatëve ndërkohë që mbani monitorimin e {entities} dhe zonës {infra}.",
            "assumptions": [
                "Kryetësi më e lartë ose partnerët mund të alokojnë mbështetje shtesë",
                "Forcat lokale ekzistuese mund të mbajnë vëzhgimin derisa të mbërrijë lehtësimi",
                "Pamja e operacionit mbetet dinamike dhe kërkon forcim të koordinuar"
            ],
            "expected_effect_template": "Ekuilibër i përmirësuar i forcave miqësore dhe reziliencë e monitorimit rreth {infra}",
            "objective_template": "Stabilizimi i qëndrimit të vigjilencës dhe kërkimi i forcimeve për {entities} pranë {infra}.",
            "rationale_template": "Zgjedhur sepse presioni i kontaktit aktual tejkalon mbështetjen miqësore të disponueshme në teatër."
        },
        "mk": {
            "title_template": "Барање на дополнителна сојузна поддршка и одржување на следење",
            "description_template": "Тековниот притисок на контактот надминува ја моментално достапната позиција на пријателска поддршка. Препорачуваме да се побара дополнително сојузно морско и ISR покриење додека се одржува следењето на {entities} и областа {infra}.",
            "assumptions": [
                "Високиот штаб или партнерите можат да доделат дополнителна поддршка",
                "Постојните локални сили можат да одржат следење додека не стигне олеснувањето",
                "Оперативната слика останува флуидна и бара координирано зајакнување"
            ],
            "expected_effect_template": "Подобрен баланс на пријателските сили и отпорност на следењето околу {infra}",
            "objective_template": "Стабилизирање на позицијата на надзорот и барање за зајакнување за {entities} покрај {infra}.",
            "rationale_template": "Избрано бидејќи притисокот на контактот моментално надминува ја пријателската поддршка достапна во театарот."
        },
        "me": {
            "title_template": "Zahtev za Dodatnu Saveznu Podršku i Održavanje Nadzora",
            "description_template": "Trenutni pritisak kontakta prevazilazi trenutno dostupni stav prijateljske podrške. Preporučuje se zahtev za dodatnu saveznu morsku i ISR pokrivenost uz održavanje nadzora {entities} i područja {infra}.",
            "assumptions": [
                "Viši štab ili partneri mogu dodeliti dodatnu podršku",
                "Postojeće lokalne snage mogu održati nadzor dok ne stigne olakšanje",
                "Operativna slika ostaje fluidna i zahteva koordinisano pojačanje"
            ],
            "expected_effect_template": "Poboljšan balans prijateljskih snaga i otpornost nadzora oko {infra}",
            "objective_template": "Stabilizovati stav nadzora i tražiti pojačanje za {entities} u blizini {infra}.",
            "rationale_template": "Odabrano jer trenutni pritisak kontakta prevazilazi dostupnu prijateljsku podršku u teatru."
        },
        "el": {
            "title_template": "Αίτημα Επιπλέον Συμμαχικής Υποστήριξης και Συνεχής Παρακολούθησης",
            "description_template": "Η τρέχουσα πίεση επαφής υπερβαίνει τη διαθέσιμη στάση υποστήριξης των φίλων. Συνιστάται η αίτηση για επιπλέον συμμαχική θαλάσσια και ISR κάλυψη διατηρώντας την παρακολούθηση των {entities} και της περιοχής {infra}.",
            "assumptions": [
                "Το ανώτερο διοικητικό σώμα ή οι συνεργάτες μπορούν να κατανομήσουν επιπλέον υποστήριξη",
                "Οι υπάρχουσες τοπικές δυνάμεις μπορούν να διατηρήσουν την παρατήρηση μέχρι να έρθει η ανακούφιση",
                "Το επιχειρησιακό εικόνα παραμένει δυναμικό και απαιτεί συντονισμένη ενίσχυση"
            ],
            "expected_effect_template": "Βελτιωμένη ισορροπία των φιλικών δυνάμεων και ανθεκτικότητα παρακολούθησης γύρω από το {infra}",
            "objective_template": "Σταθεροποίηση της στάσης επιτήρησης και αίτημα ενίσχυσης για τα {entities} κοντά στο {infra}.",
            "rationale_template": "Επιλέχθηκε επειδή η πίεση επαφής υπερβαίνει αυτή τη στιγμή τη διαθέσιμη φιλική υποστήριξη στο θάλαμο."
        }
    },
    "COA-TPL-BASELINE": {
        "en": {
            "title_template": "Maintain Baseline Monitoring",
            "description_template": "No elevated threat indicators detected. Recommend continuing routine monitoring.",
            "assumptions": [
                "No change in current threat picture"
            ],
            "expected_effect_template": "Continued situational awareness at baseline level near {infra}",
            "objective_template": "Maintain baseline awareness of {infra} and the operating area.",
            "rationale_template": "Selected because no stronger threat-matched advisory action currently dominates baseline monitoring."
        },
        "es": {
            "title_template": "Mantener vigilancia de base",
            "description_template": "No se detectan indicadores elevados de amenaza. Se recomienda continuar con la vigilancia rutinaria.",
            "assumptions": [
                "No hay cambios en la imagen actual de amenaza"
            ],
            "expected_effect_template": "Conocimiento situacional continuado a nivel base cerca de {infra}",
            "objective_template": "Mantener conocimiento base de {infra} y del área operativa.",
            "rationale_template": "Se selecciona porque ninguna acción consultiva ajustada a la amenaza supera actualmente la vigilancia de base."
        },
        "fr": {
            "title_template": "Maintenir la Surveillance de Base",
            "description_template": "Aucun indicateur de menace élevé détecté. Recommander de continuer la surveillance de routine.",
            "assumptions": [
                "Aucun changement dans le tableau de menace actuel"
            ],
            "expected_effect_template": "Maintien de la sensibilisation situationnelle au niveau de base près de {infra}",
            "objective_template": "Maintenir une sensibilisation de base de {infra} et de la zone d'opération.",
            "rationale_template": "Sélectionné car aucune action consultative correspondant à une menace plus forte ne domine actuellement la surveillance de base."
        },
        "de": {
            "title_template": "Basisüberwachung beibehalten",
            "description_template": "Keine erhöhten Bedrohungsindikatoren festgestellt. Empfiehlt die Fortsetzung der routinemäßigen Überwachung.",
            "assumptions": [
                "Keine Änderung des aktuellen Bedrohungsbildes"
            ],
            "expected_effect_template": "Fortgesetzte Lagebewusstheit auf Basisniveau in der Nähe von {infra}",
            "objective_template": "Aufrechterhaltung der Basiswahrnehmung von {infra} und dem Einsatzgebiet.",
            "rationale_template": "Ausgewählt, da keine stärker bedrohungsbezogene beratende Maßnahme derzeit die Basisüberwachung dominiert."
        },
        "it": {
            "title_template": "Mantenere il Monitoraggio di Base",
            "description_template": "Nessun indicatore di minaccia elevato rilevato. Si raccomanda di continuare il monitoraggio di routine.",
            "assumptions": [
                "Nessun cambiamento nel quadro della minaccia attuale"
            ],
            "expected_effect_template": "Continua consapevolezza situazionale al livello di base vicino a {infra}",
            "objective_template": "Mantenere la consapevolezza di base di {infra} e dell'area operativa.",
            "rationale_template": "Selezionato perché nessuna azione di avviso corrispondente a una minaccia più forte domina attualmente il monitoraggio di base."
        },
        "pt": {
            "title_template": "Manter Monitoramento de Linha de Base",
            "description_template": "Nenhum indicador de ameaça elevado detectado. Recomenda-se continuar o monitoramento de rotina.",
            "assumptions": [
                "Sem alteração no quadro de ameaças atual"
            ],
            "expected_effect_template": "Continuidade da consciência situacional no nível de linha de base perto de {infra}",
            "objective_template": "Manter a consciência de linha de base de {infra} e da área operacional.",
            "rationale_template": "Selecionado porque nenhuma ação de aconselhamento correspondente a ameaças mais forte domina atualmente o monitoramento de linha de base."
        },
        "nl": {
            "title_template": "Handhaaf Basislijn Monitoring",
            "description_template": "Geen verhoogde dreigingsindicatoren gedetecteerd. Aanbeveling om routinematige monitoring voort te zetten.",
            "assumptions": [
                "Geen verandering in het huidige dreigingsbeeld"
            ],
            "expected_effect_template": "Voortzetting van situationeel bewustzijn op basislijn niveau nabij {infra}",
            "objective_template": "Handhaven van basislijn bewustzijn van {infra} en het operationele gebied.",
            "rationale_template": "Gekozen omdat geen sterkere dreigings-gekoppelde adviesactie momenteel de basislijnmonitoring domineert."
        },
        "pl": {
            "title_template": "Utrzymanie Monitorowania Bazowego",
            "description_template": "Nie wykryto podwyższonych wskaźników zagrożenia. Rekomenduje się kontynuowanie rutynowego monitorowania.",
            "assumptions": [
                "Brak zmian w obecnym obrazie zagrożenia"
            ],
            "expected_effect_template": "Kontynuacja świadomości sytuacyjnej na poziomie bazowym w pobliżu {infra}",
            "objective_template": "Utrzymanie bazowej świadomości {infra} i obszaru operacyjnego.",
            "rationale_template": "Wybrano, ponieważ żaden silniejszy doradczy działający na podstawie zagrożenia nie dominuje obecnie w monitorowaniu bazowym."
        },
        "tr": {
            "title_template": "Temel İzlemeyi Sürdürün",
            "description_template": "Yükseltilmiş tehdit göstergeleri tespit edilmedi. Rutin izlemeye devam edilmesi tavsiye edilir.",
            "assumptions": [
                "Mevcut tehdit resminde değişiklik yok"
            ],
            "expected_effect_template": "{infra} yakınında temel düzeyde devam eden durum farkındalığı",
            "objective_template": "{infra} ve operasyonel alanın temel farkındalığını sürdürmek.",
            "rationale_template": "Seçildi çünkü temel izlemeyi baskın kılan daha güçlü bir tehdit eşleşmeli danışmanlık eylemi mevcut değildir."
        },
        "cs": {
            "title_template": "Udržovat základní monitorování",
            "description_template": "Nebyly detekovány zvýšené indikátory hrozby. Doporučuje se pokračovat v rutinním monitorování.",
            "assumptions": [
                "Žádná změna v aktuálním obraze hrozby"
            ],
            "expected_effect_template": "Pokračující situční povědomí na základní úrovni poblíž {infra}",
            "objective_template": "Udržet základní povědomí o {infra} a operační oblasti.",
            "rationale_template": "Vybráno, protože žádná silnější akce na základě hrozby v současné době nedominuje základnímu monitorování."
        },
        "ro": {
            "title_template": "Menținerea Monitorizării de Bază",
            "description_template": "Nu au fost detectate indicatori de amenințare ridicati. Se recomandă continuarea monitorizării de rutină.",
            "assumptions": [
                "Fără schimbări în imaginea actuală a amenințării"
            ],
            "expected_effect_template": "Continuarea conștiinței situaționale la nivel de bază în apropierea {infra}",
            "objective_template": "Menținerea conștiinței de bază asupra {infra} și a zonei operaționale.",
            "rationale_template": "Selectat deoarece nicio acțiune de sfatăt care să se potrivească amenințării nu domină în prezent monitorizarea de bază."
        },
        "hu": {
            "title_template": "Alapvonal Megfigyelésének Fenntartása",
            "description_template": "Nincs magas szintű fenyegetési indikátor detektálva. Ajánlott folytatni a rutin monitorozást.",
            "assumptions": [
                "Nincs változás az aktuális fenyegetési képben"
            ],
            "expected_effect_template": "Folyamatos helyzetinformáció az alapvonal szinten a {infra} közelében",
            "objective_template": "Fenntartani az alapvonal tudatosságát a {infra} és a működési terület tekintetében.",
            "rationale_template": "Ez a javaslat kiválasztásra került, mert nincs erősebb, fenyegetéshez illeszkedő tanácsadási akció, amely dominálja az alapvonal monitorozását."
        },
        "bg": {
            "title_template": "Поддържане на Базово Наблюдение",
            "description_template": "Не са открити повишени индикатори на заплаха. Препоръчва се продължаване на рутинния мониторинг.",
            "assumptions": [
                "Няма промяна в текущата картина на заплахата"
            ],
            "expected_effect_template": "Продължаваща ситуационна осведоменост на базово ниво близо до {infra}",
            "objective_template": "Поддържане на базова осведоменост за {infra} и оперативната зона.",
            "rationale_template": "Избрано, защото нито една по-силна консултативна мярка, съответстваща на заплахата, не доминира в момента в базовия мониторинг."
        },
        "hr": {
            "title_template": "Održavanje Osnovnog Nadzora",
            "description_template": "Nije detektirano podignuta indikacija prijetnje. Preporučuje se nastavak rutinskog nadzora.",
            "assumptions": [
                "Nema promjene u trenutnoj slici prijetnje"
            ],
            "expected_effect_template": "Nastavak situacijske svijesti na osnovnom nivou u blizini {infra}",
            "objective_template": "Održavanje osnovne svijesti o {infra} i operativnom području.",
            "rationale_template": "Odabrano jer trenutno nijedna jača akcija savjetovanja usklađena s prijetnjom ne dominira osnovnim nadzorom."
        },
        "sk": {
            "title_template": "Udržať základné monitorovanie",
            "description_template": "Neodetekované zvýšené ukazovatele hrozby. Odporúča sa pokračovať v rutinnom monitorovaní.",
            "assumptions": [
                "Žiadna zmena v aktuálnom obraze hrozby"
            ],
            "expected_effect_template": "Pokračujúce situčné povedomie na základnej úrovni blízko {infra}",
            "objective_template": "Udržať základné povedomie o {infra} a operačnej oblasti.",
            "rationale_template": "Vybrané, pretože žiadna silnejšia akcia poradenstva zodpovedajúca hrozbe momentálne nedominuje základnému monitorovaniu."
        },
        "sl": {
            "title_template": "Ohranitev osnovnega nadzora",
            "description_template": "Ne je odkriveno povečano indikatorje amebe. Priporoča se nadaljevanje rutinskega nadzora.",
            "assumptions": [
                "Brez sprememb v trenutni sliki amebe"
            ],
            "expected_effect_template": "Nadaljnje situacijsko obvestitev na osnovnem nivoju blizu {infra}",
            "objective_template": "Ohraniti osnovno obvestitev o {infra} in operativnem območju.",
            "rationale_template": "Izbrano, ker trenutno ne dominira noben močnejši odziv, usklajen z amebo, nad osnovnim nadzorom."
        },
        "et": {
            "title_template": "Säilitada põhiline jälgimine",
            "description_template": "Ei tuvastatud tõstetud ohtlikke näitajaid. Soovitatakse jätkata rutinemäeste jälgimist.",
            "assumptions": [
                "Ei muutust praeguses ohtlikus pildis"
            ],
            "expected_effect_template": "Jätkunud olukorda teadlikkus põhiline taseme {infra} läheduses",
            "objective_template": "Säilitada põhiline teadlikkus {infra} ja operatsiooniala kohta.",
            "rationale_template": "Valitud, sest ei ole praegu võimsamat ohtlikuse vastav nõuande tegevust, mis domineeriks põhiline jälgimine."
        },
        "lv": {
            "title_template": "Saglabāt bāzes uzraudzību",
            "description_template": "Nav detectēti paaugstināti draudens indikatori. Ieteicams turpināt rutīnas uzraudzību.",
            "assumptions": [
                "Nav izmaiņu pašreizējā draudens attēla"
            ],
            "expected_effect_template": "Turpināt situācijas zināšanu bāzes līmenī tuvumā {infra}",
            "objective_template": "Saglabāt bāzes zināšanu par {infra} un operācijas teritoriju.",
            "rationale_template": "Izvēlēts, jo nav spēcīgāka draudens atbilstīga padomus darbība, kas pašlaik dominē bāzes uzraudzībā."
        },
        "lt": {
            "title_template": "Išlaikyti Bazinį Stebėjimo",
            "description_template": "Nepastebėti didelės grėsmės rodiklių. Regaliam tęsti rutininį stebėjimą.",
            "assumptions": [
                "Negalimas pokyčio dabartiniame grėsmės vaizde"
            ],
            "expected_effect_template": "Tęsiama situacijos supratimas bazinio lygio prie {infra}",
            "objective_template": "Išlaikyti bazinį supratimą apie {infra} ir operavimo teritoriją.",
            "rationale_template": "Pasirinkta, nes jokia stipresnė grėsmės atitinkanti patarimų veikla šiuo metu dominuoja bazinio stebėjimo."
        },
        "da": {
            "title_template": "Oprethold Basislinje Overvågning",
            "description_template": "Ingen forhøjede trusselsindikatorer detekteret. Anbefaler fortsat rutinemæssig overvågning.",
            "assumptions": [
                "Ingen ændring i det nuværende trusselsbillede"
            ],
            "expected_effect_template": "Fortsat situationsfornemmelse på basislinjeniveau nær {infra}",
            "objective_template": "Oprethold basislinjebevidsthed om {infra} og driftsområdet.",
            "rationale_template": "Valgt, fordi ingen stærkere trusselsmatchet rådgivningshandling i øjeblikket dominerer basislinjeovervågningen."
        },
        "no": {
            "title_template": "Opprettholde grunnlinjeovervåking",
            "description_template": "Ingen forhøyede trusselindikatorer oppdaget. Anbefaler å fortsette rutinemessig overvåking.",
            "assumptions": [
                "Ingen endring i det nåværende trusselbildet"
            ],
            "expected_effect_template": "Fortsatt situasjonsforståelse på grunnlinjenivå nær {infra}",
            "objective_template": "Opprettholde grunnlinjebevissthet om {infra} og operasjonsområdet.",
            "rationale_template": "Valgt fordi ingen sterkere trussel-matchet rådgivningshandling for tiden dominerer grunnlinjeovervåkingen."
        },
        "is": {
            "title_template": "Halda grundvallar eftirliti",
            "description_template": "Engin aukna hættuleg merki uppgötvað. Mætir með að halda áfram við rutínum eftirlit.",
            "assumptions": [
                "Engin breyting í núverandi hættulegum mynd"
            ],
            "expected_effect_template": "Stöðug varkárni á grundvallarstigi nær {infra}",
            "objective_template": "Halda grundvallar varkárni á {infra} og virkni svæðinu.",
            "rationale_template": "Valinn því að engin sterkari hættuleg ráðgjafastöðu domínar núverandi grundvallar eftirlit."
        },
        "fi": {
            "title_template": "Ylläpidä perusvalvontaa",
            "description_template": "Ei havaittu kohonneita uhkaindikaattoreita. Suositellaan rutiininomaisen seurannan jatkamista.",
            "assumptions": [
                "Ei muutosta nykyisessä uhkakuvassa"
            ],
            "expected_effect_template": "Jatkuva tilannetietoisuus peruskorokkeella {infra}:n lähellä",
            "objective_template": "Ylläpidä perusvalppaus {infra}:n ja toiminta-alueen suhteen.",
            "rationale_template": "Valittu, koska voimakkaampi uhkaan vastaava neuvontatoimi ei tällä hetkellä dominoi perusvalvontaa."
        },
        "sv": {
            "title_template": "Bibehåll baslinjeövervakning",
            "description_template": "Inga förhöjda hotindikatorer detekterade. Rekommenderar fortsatt rutinmässig övervakning.",
            "assumptions": [
                "Ingen förändring i nuvarande hotbild"
            ],
            "expected_effect_template": "Fortsatt situationsmedvetenhet på baslinjenivå nära {infra}",
            "objective_template": "Bibehålla baslinje medvetenhet om {infra} och operationsområdet.",
            "rationale_template": "Vald eftersom ingen starkare hotmatchad rådgivningsåtgärd för närvarande dominerar baslinjeövervakningen."
        },
        "sq": {
            "title_template": "Mbani Monitorimin Bazë",
            "description_template": "Nuk janë zbuluar tregues të rritur të kërcënimit. Rekomandojmë vazhdimin e monitorimit rutinë.",
            "assumptions": [
                "Asnjë ndryshim në panoramën aktuale të kërcënimit"
            ],
            "expected_effect_template": "Ndërgjegjësim i vazhdueshëm në nivel bazë pranë {infra}",
            "objective_template": "Mbani ndërgjegjësimin bazë të {infra} dhe zonës operative.",
            "rationale_template": "Zgjedhur sepse asnjë veprim këshillues me kërcënim më të fortë nuk dominoi aktualisht monitorimin bazë."
        },
        "mk": {
            "title_template": "Одржување на базната следење",
            "description_template": "Не се детектирале повишени индикатори на закана. Препорачуваме продолжување на рутинското следење.",
            "assumptions": [
                "Нема промена во тековната слика на заканата"
            ],
            "expected_effect_template": "Континуирано ситуационална свесност на базен ниво покрај {infra}",
            "objective_template": "Одржување базна свесност за {infra} и оперативната област.",
            "rationale_template": "Избрано бидејќи нема посилен советувачки акција совпадната со заканата која доминира над базната свесност."
        },
        "me": {
            "title_template": "Održavanje Osnovnog Nadzora",
            "description_template": "Nisu detektovani podignuti indikatori pretnje. Preporučuje se nastavak rutinskog nadzora.",
            "assumptions": [
                "Nema promene u trenutnoj slici pretnje"
            ],
            "expected_effect_template": "Nastavak situacione svesti na osnovnom nivou u blizini {infra}",
            "objective_template": "Održavanje osnovne svesti o {infra} i operativnom području.",
            "rationale_template": "Odabrano jer trenutno nijedna akcija savetovanja usklađena sa pretnjom ne dominira osnovnim nadzorom."
        },
        "el": {
            "title_template": "Διατήρηση Βασικής Παρακολούθησης",
            "description_template": "Δεν ανιχνεύονται αυξημένα δείκτες απειλής. Συνιστάται η συνέχιση της ρουτινής παρακολούθησης.",
            "assumptions": [
                "Καμία αλλαγή στην τρέχουσα εικόνα της απειλής"
            ],
            "expected_effect_template": "Συνεχής ситуационная ενημέρωση στο βασικό επίπεδο κοντά στο {infra}",
            "objective_template": "Διατήρηση της βασικής ενημέρωσης για το {infra} και την επιχειρησιακή περιοχή.",
            "rationale_template": "Επιλέχθηκε επειδή καμία πιο ισχυρή συμβουλευτική δράση που αντιστοιχεί στην απειλή δεν κυριαρχεί αυτή τη στιγμή στην βασική παρακολούθηση."
        }
    }
}

PLAN_PACKAGE_TRANSLATIONS: dict[str, dict[str, object]] = {
    "en": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Establish shadow track",
                    "description": "Maintain visual/radar contact at safe distance and report pattern changes.",
                    "preconditions": [
                        "Maritime asset on station"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Deploy ISR collection",
                    "description": "Launch UAV and request supporting remote sensing over the operating corridor.",
                    "preconditions": [
                        "Weather permits ISR collection"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Protect cable corridor",
                    "description": "Maintain patrol and integrity monitoring over the remaining cable route.",
                    "preconditions": [
                        "Patrol asset can hold station near infrastructure"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordinate civil airspace",
                    "description": "Set temporary procedures with civil aviation actors and distribute sensor cues.",
                    "preconditions": [
                        "Civil aviation authority reachable"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Increase border monitoring",
                    "description": "Coordinate surveillance and reporting over convoy approaches and crossings.",
                    "preconditions": [
                        "Border patrol liaison available"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordinate package branches and deconflict scarce assets",
        "finish_to_start_condition": "Prior task establishes the required observation picture",
        "conditional_condition": "Escalate later package actions only if monitoring confirms persistence or approach",
        "package_title": "Coordinated package for {titles}",
        "package_summary": "Sequenced advisory package with task dependencies, explicit asset reservation, and branch coordination across the selected COAs."
    },
    "es": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Establecer seguimiento en sombra",
                    "description": "Mantener contacto visual/radar a distancia de seguridad e informar cambios de patrón.",
                    "preconditions": [
                        "Medio marítimo en estación"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Desplegar recogida ISR",
                    "description": "Lanzar UAV y solicitar sensores remotos de apoyo sobre el corredor operativo.",
                    "preconditions": [
                        "La meteorología permite recogida ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Proteger corredor de cable",
                    "description": "Mantener patrulla y monitorización de integridad sobre la ruta de cable restante.",
                    "preconditions": [
                        "El medio de patrulla puede mantenerse cerca de la infraestructura"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordinar espacio aéreo civil",
                    "description": "Establecer procedimientos temporales con actores de aviación civil y distribuir indicaciones de sensores.",
                    "preconditions": [
                        "Autoridad de aviación civil accesible"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Incrementar vigilancia fronteriza",
                    "description": "Coordinar vigilancia e informes sobre aproximaciones y cruces de convoyes.",
                    "preconditions": [
                        "Enlace de patrulla fronteriza disponible"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordinar ramas del paquete y descongestionar medios escasos",
        "finish_to_start_condition": "La tarea previa establece la imagen de observación necesaria",
        "conditional_condition": "Escalar acciones posteriores del paquete solo si la vigilancia confirma persistencia o aproximación",
        "package_title": "Paquete coordinado para {titles}",
        "package_summary": "Paquete consultivo secuenciado con dependencias entre tareas, reserva explícita de medios y coordinación de ramas entre las COAs seleccionadas."
    },
    "fr": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Établir une piste d'ombre",
                    "description": "Maintenir le contact visuel/radar à distance de sécurité et signaler les changements de schéma.",
                    "preconditions": [
                        "Actif maritime en poste"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Déployer la collecte ISR",
                    "description": "Lancer un UAV et demander une télédétection de soutien sur le corridor d'opération.",
                    "preconditions": [
                        "La météo permet la collecte ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Protéger le corridor du câble",
                    "description": "Maintenir la patrouille et la surveillance de l'intégrité sur le tracé de câble restant.",
                    "preconditions": [
                        "L'actif de patrouille peut maintenir sa position près de l'infrastructure"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordonner l'espace aérien civil",
                    "description": "Établir des procédures temporaires avec les acteurs de l'aviation civile et distribuer les signaux de capteurs.",
                    "preconditions": [
                        "Autorité de l'aviation civile joignable"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Augmenter la surveillance des frontières",
                    "description": "Coordonner la surveillance et le rapport sur les approches et les passages des convois.",
                    "preconditions": [
                        "Liaison de patrouille des frontières disponible"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordonner les branches de paquet et désengorger les actifs rares",
        "finish_to_start_condition": "La tâche précédente établit le tableau d'observation requis",
        "conditional_condition": "Escalader les actions du paquet ultérieur seulement si la surveillance confirme la persistance ou l'approche",
        "package_title": "Paquet coordonné pour {titles}",
        "package_summary": "Paquet consultatif séquencé avec dépendances de tâches, réservation explicite d'actifs et coordination des branches à travers les COA sélectionnés."
    },
    "de": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Schattenverfolgung einrichten",
                    "description": "Visuellen/Radar-Kontakt in sicherer Entfernung aufrechterhalten und Musteränderungen melden.",
                    "preconditions": [
                        "Maritimes Asset an Station"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "ISR-Erfassung einsetzen",
                    "description": "UAV starten und unterstützende Fernerkundung über dem Betriebskorridor anfordern.",
                    "preconditions": [
                        "Wetter erlaubt ISR-Erfassung"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Kabelkorridor schützen",
                    "description": "Patrouille und Integritätsüberwachung über die verbleibende Kabelstrecke aufrechterhalten.",
                    "preconditions": [
                        "Patrouillen-Asset kann nahe der Infrastruktur stationieren"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Ziviler Luftraum koordinieren",
                    "description": "Temporäre Verfahren mit zivilen Luftfahrtakteuren festlegen und Sensorkennzeichen verteilen.",
                    "preconditions": [
                        "Zivile Luftfahrtbehörde erreichbar"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Grenzwachsamkeit erhöhen",
                    "description": "Überwachung und Meldung über Konvoiankünfte und -querungen koordinieren.",
                    "preconditions": [
                        "Grenztruppen-Liaison verfügbar"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Paketzweige koordinieren und knappe Ressourcen entkonfliktieren",
        "finish_to_start_condition": "Vorherige Aufgabe etabliert das erforderliche Beobachtungsbild",
        "conditional_condition": "Spätere Paketaktionen nur eskalieren, wenn die Überwachung Persistenz oder Annäherung bestätigt",
        "package_title": "Koordiniertes Paket für {titles}",
        "package_summary": "Sequenziertes Beratungspaket mit Aufgabenabhängigkeiten, expliziter Ressourcenreservierung und Zweigkoordination über die ausgewählten COAs."
    },
    "it": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Stabilire tracciamento di ombra",
                    "description": "Mantenere contatto visivo/radar a distanza di sicurezza e segnalare i cambiamenti di pattern.",
                    "preconditions": [
                        "Asset marittimo in posizione"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Schierare raccolta ISR",
                    "description": "Lanciare UAV e richiedere telerilevamento di supporto lungo il corridoio operativo.",
                    "preconditions": [
                        "Il meteo consente la raccolta ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Proteggere corridoio cavo",
                    "description": "Mantenere pattugliamento e monitoraggio dell'integrità lungo il percorso del cavo rimanente.",
                    "preconditions": [
                        "L'asset di pattugliamento può mantenere la posizione vicino alle infrastrutture"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordinare spazio aereo civile",
                    "description": "Stabilire procedure temporanee con gli attori dell'aviazione civile e distribuire segnali di sensori.",
                    "preconditions": [
                        "Autorità aeronautica civile raggiungibile"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Aumentare monitoraggio confine",
                    "description": "Coordinare sorveglianza e segnalazione sugli avvicinamenti e attraversamenti dei convogli.",
                    "preconditions": [
                        "Disponibile collegamento con la pattuglia di confine"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordinare i rami del pacchetto e deconflittare gli asset scarsi",
        "finish_to_start_condition": "Il compito precedente stabilisce il quadro osservativo richiesto",
        "conditional_condition": "Escalare le azioni del pacchetto successivo solo se il monitoraggio conferma persistenza o avvicinamento",
        "package_title": "Pacchetto coordinato per {titles}",
        "package_summary": "Pacchetto di avviso sequenziato con dipendenze di compito, riserva esplicita di asset e coordinamento dei rami attraverso i COA selezionati."
    },
    "pt": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Estabelecer rastreamento de sombra",
                    "description": "Manter contato visual/radar a distância segura e relatar mudanças no padrão.",
                    "preconditions": [
                        "Ativo marítimo na estação"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Implementar coleta ISR",
                    "description": "Lançar UAV e solicitar sensoriamento remoto de apoio sobre o corredor de operação.",
                    "preconditions": [
                        "Clima permite coleta ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Proteger corredor do cabo",
                    "description": "Manter patrulha e monitoramento de integridade sobre a rota do cabo restante.",
                    "preconditions": [
                        "Ativo de patrulha pode manter estação perto da infraestrutura"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordenar espaço aéreo civil",
                    "description": "Estabelecer procedimentos temporários com atores da aviação civil e distribuir pistas de sensores.",
                    "preconditions": [
                        "Autoridade de aviação civil alcançável"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Aumentar monitoramento de fronteira",
                    "description": "Coordenar vigilância e relatórios sobre aproximações e travessias de comboios.",
                    "preconditions": [
                        "Ligação de patrulha de fronteira disponível"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordenar ramificações de pacotes e desconflitar ativos escassos",
        "finish_to_start_condition": "Tarefa anterior estabelece o quadro de observação necessário",
        "conditional_condition": "Escalar ações de pacotes posteriores somente se o monitoramento confirmar persistência ou aproximação",
        "package_title": "Pacote coordenado para {titles}",
        "package_summary": "Pacote de aconselhamento sequenciado com dependências de tarefas, reserva explícita de ativos e coordenação de ramificações através dos COAs selecionados."
    },
    "nl": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Schaduwspoor vaststellen",
                    "description": "Visueel/radar contact behouden op veilige afstand en patroonwijzigingen rapporteren.",
                    "preconditions": [
                        "Maritiem actief op post"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "ISR-inzameling inzetten",
                    "description": "UAV lanceren en ondersteunende remote sensing aanvragen over de operationele corridor.",
                    "preconditions": [
                        "Weer staat ISR-inzameling toe"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Kabellijn beschermen",
                    "description": "Patrouille en integriteitsmonitoring handhaven over de resterende kabellijn.",
                    "preconditions": [
                        "Patrouilleactief kan post vasthouden nabij infrastructuur"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Civiele luchtruimte coördineren",
                    "description": "Tijdelijke procedures vaststellen met civiele luchtvaartactoren en sensorschijfjes distribueren.",
                    "preconditions": [
                        "Civiele luchtvaartautoriteit bereikbaar"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Grensbewaking verhogen",
                    "description": "Toezicht en rapportage coördineren over konvooiaankomsten en -overgangen.",
                    "preconditions": [
                        "Grenspatrouille liaison beschikbaar"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Pakketvertakkingen coördineren en schaarse middelen ontwarren",
        "finish_to_start_condition": "Voorgaande taak stelt het vereiste observatiebeeld vast",
        "conditional_condition": "Latere pakketacties escaleren alleen als monitoring persistentie of nadering bevestigt",
        "package_title": "Gecoördineerd pakket voor {titles}",
        "package_summary": "Geordend adviespakket met taakafhankelijkheden, expliciete middelenreservering en vertakkingscoördinatie over de geselecteerde COA's."
    },
    "pl": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Ustanowienie śledzenia cieniowego",
                    "description": "Utrzymywanie kontaktu wizualnego/radarowego w bezpiecznej odległości i raportowanie zmian w wzorcu.",
                    "preconditions": [
                        "Aktywa morskie na stanowisku"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Wdrożenie zbierania ISR",
                    "description": "Uruchomienie UAV i żądanie wsparcia teledetekcyjnego nad korytarzem operacyjnym.",
                    "preconditions": [
                        "Warunki pogodowe pozwalają na zbieranie ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Ochrona korytarza kablowego",
                    "description": "Utrzymywanie patrolu i monitorowania integralności nad pozostałą trasą kabla.",
                    "preconditions": [
                        "Aktywo patrolowe może utrzymać stanowisko w pobliżu infrastruktury"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordynacja przestrzeni powietrznej cywilnej",
                    "description": "Ustalenie tymczasowych procedur z aktorami lotnictwa cywilnego i dystrybucja sygnałów czujników.",
                    "preconditions": [
                        "Organ lotnictwa cywilnego jest dostępny"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Zwiększenie monitorowania granicy",
                    "description": "Koordynacja nadzoru i raportowania nad zbliżeniami i przekroczeniami konwojów.",
                    "preconditions": [
                        "Dostępny łącznik patrolowy graniczny"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordynacja gałęzi pakietu i rozstrzyganie konfliktów rzadkich zasobów",
        "finish_to_start_condition": "Poprzednie zadanie ustanawia wymagany obraz obserwacyjny",
        "conditional_condition": "Eskalacja działań późniejszego pakietu tylko jeśli monitorowanie potwierdza uporczywość lub zbliżanie się",
        "package_title": "Zkoordynowany pakiet dla {titles}",
        "package_summary": "Sekwencyjny pakiet doradczy z zależnościami zadań, wyraźną rezerwacją zasobów i koordynacją gałęzi w wybranych COA."
    },
    "tr": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Gölge takibi kur",
                    "description": "Güvenli mesafede görsel/radar temasını sürdür ve desen değişikliklerini raporla.",
                    "preconditions": [
                        "Deniz unsuru görevde"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "ISR toplama konuşlandır",
                    "description": "İHA fırlat ve operasyon koridoru üzerinde destekleyici uzaktan algılama talep et.",
                    "preconditions": [
                        "Hava durumu ISR toplamasını sağlıyor"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Kablo koridorunu koru",
                    "description": "Kalan kablo güzergahı üzerinde devriye ve bütünlük izlemesini sürdür.",
                    "preconditions": [
                        "Devriye unsuru altyapı yakınında görevde kalabilir"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Sivil hava sahasını koordine et",
                    "description": "Sivil havacılık aktörleriyle geçici prosedürler belirle ve sensör ipuçları dağıt.",
                    "preconditions": [
                        "Sivil havacılık otoritesi ulaşılabilir"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Sınır gözetimini artır",
                    "description": "Kervan yaklaşmaları ve geçişleri üzerinde gözetim ve raporlama koordine et.",
                    "preconditions": [
                        "Sınır devriye bağlantısı mevcut"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Paket dallarını koordine et ve kıt kaynakları çakışmasız hale getir",
        "finish_to_start_condition": "Ön görev gerekli gözlem resmini oluşturur",
        "conditional_condition": "İzleme sürekliliğini veya yaklaşmayı onaylarsa sonraki paket eylemlerini yükselt",
        "package_title": "{titles} için Koordineli Paket",
        "package_summary": "Seçilen COA'lar genelinde görev bağımlılıkları, açık kaynak tahsisi ve dal koordinasyonu içeren sıralı danışmanlık paketi."
    },
    "cs": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Zajišťovat stínový sled",
                    "description": "Udržovat vizuální/radarový kontakt v bezpečné vzdálenosti a hlášit změny vzoru.",
                    "preconditions": [
                        "Maritýmský prostředek na stanovišti"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Nasadit sběr ISR",
                    "description": "Spustit UAV a požádat o podporované vzdálené snímání nad operačním koridorem.",
                    "preconditions": [
                        "Počasí umožňuje sběr ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Chránit kabelový koridor",
                    "description": "Udržovat patroly a monitorování integrity nad zbývající trasou kabelu.",
                    "preconditions": [
                        "Patrolní prostředek může udržet stanoviště poblíž infrastruktury"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinovat civilní vzdušný prostor",
                    "description": "Stanovit dočasné postupy s aktéry civilní letectví a distribuovat senzory.",
                    "preconditions": [
                        "Civilní letecká autorita je dostupná"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Zvýšit monitorování hranic",
                    "description": "Koordinovat dohled a hlášení nad přibývacími a přechodmi konvojů.",
                    "preconditions": [
                        "Dostupnost spojence hranicní patroly"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinovat větve balíčku a dekonflikovat vzácné zdroje",
        "finish_to_start_condition": "Předchozí úkol stanoví požadovaný obraz pozorování",
        "conditional_condition": "Eskalovat akce pozdějších balíčků pouze v případě, že monitorování potvrdí trvalost nebo přiblížení",
        "package_title": "Koordinovaný balíček pro {titles}",
        "package_summary": "Sekvenční poradní balíček s závislostmi úkolů, explicitní rezervací zdrojů a koordinací větve napříč vybranými COA."
    },
    "ro": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Stabilirea urmăririi umbrei",
                    "description": "Menținerea contactului vizual/radar la distanță sigură și raportarea schimbărilor de tipare.",
                    "preconditions": [
                        "Activul maritim la stație"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Implementarea colectării ISR",
                    "description": "Lansarea UAV-ului și solicitarea de teledetecție de suport deasupra coridorului de operare.",
                    "preconditions": [
                        "Condițiile meteo permit colectarea ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Protejarea coridorului cablului",
                    "description": "Menținerea patrulei și monitorizarea integrității pe traseul rămas al cablului.",
                    "preconditions": [
                        "Activul de patrulare poate menține stația lângă infrastructură"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Coordonarea spațiului aerian civil",
                    "description": "Stabilirea procedurilor temporare cu actorii aviației civile și distribuirea semnalelor de senzori.",
                    "preconditions": [
                        "Autoritatea aviației civile este accesibilă"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Creșterea monitorizării frontierei",
                    "description": "Coordonarea supravegherii și a raportării asupra abordărilor și traversărilor convoaielor.",
                    "preconditions": [
                        "Liaison de patrulare a frontierei este disponibil"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Coordonarea ramurilor pachetului și deconflictarea activelor escare",
        "finish_to_start_condition": "Sarcina anterioară stabilește imaginea de observare necesară",
        "conditional_condition": "Escalarea acțiunilor pachetului ulterior doar dacă monitorizarea confirmă persistența sau abordarea",
        "package_title": "Pachet coordonat pentru {titles}",
        "package_summary": "Pachet de sfaturi secvențializat cu dependențe de sarcini, rezervare explicită a activelor și coordonare a ramurilor pe COA-urile selectate."
    },
    "hu": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Árnytrack kialakítása",
                    "description": "Vizualis/radar kapcsolat fenntartása biztonságos távolságon és a mintázat változásainak jelentése.",
                    "preconditions": [
                        "Tengeri eszköz állomáson"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "ISR gyűjtés bevetése",
                    "description": "UAV elindítása és támogató távérzékelés kérése az üzemeltetési korridor felett.",
                    "preconditions": [
                        "Az időjárás engedi az ISR gyűjtést"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Kábelkorridor védelme",
                    "description": "Párolás és integritás-monitorozás fenntartása a fennmaradó kábelútvonalon.",
                    "preconditions": [
                        "A párolási eszköz képes állomáson tartani az infrastruktúra közelében"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Polgári légtér koordinálása",
                    "description": "Ideiglenes eljárások megállapítása a polgári légi aktőrökkel és szenzorjelzések kiosztása.",
                    "preconditions": [
                        "Elérhető a polgári légi hatóság"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Határfelügyelet növelése",
                    "description": "Felügyelet és jelentés koordinálása a konvojok megközelítései és átlépései felett.",
                    "preconditions": [
                        "Határpárolási kapcsolattartó elérhető"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinálja a csomag ágait és csökkentse a hiányos eszközök konfliktusát",
        "finish_to_start_condition": "Az előző feladat biztosítja a szükséges megfigyelési képet",
        "conditional_condition": "Csak akkor eskalálja a későbbi csomag műveleteit, ha a monitorozás megerősíti a kitartást vagy a megközelítést",
        "package_title": "{titles} koordinált csomagja",
        "package_summary": "Sorrendezett tanácsadó csomag feladatfüggőségekkel, kifejezett eszközrezervációval és ág-koordinációval a kiválasztott COA-k között."
    },
    "bg": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Установяване на следящ път",
                    "description": "Поддържане на визуално/радарно наблюдение на безопасна дистанция и докладване на промени в модела.",
                    "preconditions": [
                        "Морско средство на позиция"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Разполагане на ISR събиране",
                    "description": "Изстрелване на БПЛА и изискване за подкрепящо дистанционно наблюдение над оперативния коридор.",
                    "preconditions": [
                        "Времето позволява ISR събиране"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Защита на кабелния коридор",
                    "description": "Поддържане на патрулиране и мониторинг на цялост на останалата кабелна траса.",
                    "preconditions": [
                        "Патрулиращо средство може да поддържа позиция близо до инфраструктурата"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Координация на гражданското въздушно пространство",
                    "description": "Установяване на временни процедури с актьори от гражданската авиация и разпределяне на сензорни сигнали.",
                    "preconditions": [
                        "Гражданската авиационна управа е достъпна"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Увеличаване на граничния мониторинг",
                    "description": "Координация на наблюдение и докладване над приближавания и пресичания на конвои.",
                    "preconditions": [
                        "Налично е звено за граничен патрул"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Координация на клоновете на пакета и деконфликтиране на ограничените ресурси",
        "finish_to_start_condition": "Предходната задача установява необходимата картина на наблюдението",
        "conditional_condition": "Ескалиране на действията на по-късните пакети само ако мониторингът потвърди устойчивост или приближаване",
        "package_title": "Координиран пакет за {titles}",
        "package_summary": "Последователен съветен пакет с зависимости на задачи, изрично резервиране на ресурси и координация на клоновете през избраните COA."
    },
    "hr": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Uspostaviti sjenu tragu",
                    "description": "Održavati vizualni/radarski kontakt na sigurnoj udaljenosti i izvještavati o promjenama obrasca.",
                    "preconditions": [
                        "Morski aktiv na stanici"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Uspostaviti ISR prikupljanje",
                    "description": "Pokrenuti UAV i zatražiti podršku daljinskog senzorskog nadzora nad operativnim koridorom.",
                    "preconditions": [
                        "Vrijeme dopušta ISR prikupljanje"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Zaštititi kabelski koridor",
                    "description": "Održavati patrolu i nadzor integriteta nad preostalim kabelskim rutama.",
                    "preconditions": [
                        "Patrolni aktiv može zadržati stanicu blizu infrastrukture"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinirati civilno zračni prostor",
                    "description": "Postaviti privremene procedure s akterima civilne avijacije i distribuirati senzorske signale.",
                    "preconditions": [
                        "Civilna aviacijska vlast dostižna"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Povećati nadzor granice",
                    "description": "Koordinirati nadzor i izvještavanje nad pristancima i prelazima konvoja.",
                    "preconditions": [
                        "Dostupan je kontakt za graničku patrolu"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinirati grane paketa i dekonfliktirati oskudne resurse",
        "finish_to_start_condition": "Prethodni zadatak uspostavlja potrebnu sliku nadzora",
        "conditional_condition": "Eskalirati rad paketa kasnije samo ako nadzor potvrdi upornost ili približavanje",
        "package_title": "Koordinirani paket za {titles}",
        "package_summary": "Sekvencirani paket savjeta s ovisnostima zadataka, eksplicitnom rezervacijom resursa i koordinacijom grana kroz odabrane COA."
    },
    "sk": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Ustanoviť tieniaci sledovanie",
                    "description": "Udržiavať vizuálny/radarový kontakt na bezpečnej vzdialenosti a hlásiť zmeny vzoru.",
                    "preconditions": [
                        "Morské aktivo na stanici"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Nasadiť zber ISR",
                    "description": "Uveľiť UAV a požiadať o podporné diaľkové meranie nad operačným koridorom.",
                    "preconditions": [
                        "Počasie umožňuje zber ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Chrániť kábelový koridor",
                    "description": "Udržiavať patroly a monitorovanie integrity zvyšnej trasy kábla.",
                    "preconditions": [
                        "Patrolné aktivo môže držať stanicu blízko infraštruktúry"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinovať civilné vzdušné prostredie",
                    "description": "Nastaviť dočasné postupy s aktérmi civilnej leteckej dopravy a distribuovať senzorové signály.",
                    "preconditions": [
                        "Civilná letecká autorita je dostupná"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Zvýšiť monitorovanie hraníc",
                    "description": "Koordinovať sledovanie a hlásenie pri príchodoch a prechodoch konvojov.",
                    "preconditions": [
                        "Dostupnosť spojenia hranícnej patroly"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinovať vetvy balíka a vyhnúť sa konfliktu nedostatkových aktív",
        "finish_to_start_condition": "Predchádzajúce úloha ustanovuje požadovaný obraz pozorovania",
        "conditional_condition": "Eskalovať akcie neskorších balíkov len v prípade, ak monitorovanie potvrdí trvanlivosť alebo príchod",
        "package_title": "Koordinovaný balík pre {titles}",
        "package_summary": "Sekvenčný poradcovský balík s závislosťou úloh, explicitnou rezerváciou aktív a koordináciou vetví naprieč vybranými COA."
    },
    "sl": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Ustanoviti senčno sledenje",
                    "description": "Ohraniti vizualni/radarski stik na varnem oddaljenosti in poročati o spremembah vzorca.",
                    "preconditions": [
                        "Morski aktiv na postaji"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Razpostaviti zbiranje ISR",
                    "description": "Začeti z letelno dronom (UAV) in zahtevati podporno odzemno opazovanje nad operativnim koridorjem.",
                    "preconditions": [
                        "Vreme omogoča zbiranje ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Zaščititi kabeljski koridor",
                    "description": "Ohraniti patrole in nadzor integritete nad preostalim kabeljskim poti.",
                    "preconditions": [
                        "Patrolni aktiv lahko drži postajo blizu infrastrukture"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinirati civilno zračnega gibanje",
                    "description": "Določiti začasne postopke z civilnimi zračnimi aktorji in distribuirati senzorne znakove.",
                    "preconditions": [
                        "Civilna zračna uprava je dostopna"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Povečati nadzor meje",
                    "description": "Koordinirati nadzor in poročanje pri približevanju in prehodu konvojev.",
                    "preconditions": [
                        "Dostopno je povezovanje mejne patrole"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinirati razboje paketa in dekonfliktirati redke vire",
        "finish_to_start_condition": "Predhodni zadatek ustvari zahtevano sliko opažanja",
        "conditional_condition": "Eskalirati kasnejše dejavnosti paketa le če potrjuje nadzor trajnost ali približevanje",
        "package_title": "Koordiniran paket za {titles}",
        "package_summary": "Sekvenciran svetovalni paket z odvisnostmi zadankov, izrecnim rezerviranjem virov in koordinacijo razbojev po izbranih COA."
    },
    "et": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Väga varju-uuring",
                    "description": "Hoida visuaalset/radaaripikaidust ja aru anda mudelimuutmistest.",
                    "preconditions": [
                        "Mereasset stantsionaalhes"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Käivita ISR kogumine",
                    "description": "Läheta UAV ja taotada tugiande kaugseantseva teatave kogumist töövöökoridori üle.",
                    "preconditions": [
                        "Ilmastik lubab ISR kogumise"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Kaabelikoridori kaitse",
                    "description": "Hoida patroll ja terviklikkuse jälgimine jäljüvas kaabeliruutu üle.",
                    "preconditions": [
                        "Patrollasset saab hoida stantsiooni infrastruktuuri lähedal"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordineerda tsiviililugemaa",
                    "description": "Määritada ajutised protseduurid tsiviililineaarilinektoritega ja levitada sensorivõimendusi.",
                    "preconditions": [
                        "Tsiviililineaarilinektor on kontaktis"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Täpsustada piirivalvust",
                    "description": "Koordineerida valvust ja aruandmist konvooji lähenemiste ja läbiminevate kohta.",
                    "preconditions": [
                        "Piirivalve kontaktis on saadaval"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordineerida paketi oksad ja dekonflikteerida harvaid ressursse",
        "finish_to_start_condition": "Eelneva ülesanne püstitab vajaliku vaatlemise pildi",
        "conditional_condition": "Eskalatsioon hilisemates paketi tegevustel ainult siis, kui jälgimine kinnitab pidevust või lähenemist",
        "package_title": "Koordineeritud pakett {titles}",
        "package_summary": "Järjestatud nõuandepakett ülesannete sõltuvustega, selge ressursi varasemist ja oksade koordineerimist valitud COA-de läbikaudu."
    },
    "lv": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Izveidot deltas izsekot",
                    "description": "Uzturēt vizuālo/radara kontaktu drošā attāluma un ziņot par secinājuma izmaiņām.",
                    "preconditions": [
                        "Jūras aktīvs uz stacijas"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Ieviekt ISR datu savākšanu",
                    "description": "Izlemt UAV un pieprasīt atbalstošu tālvadības sensorišu pārbaudi darbības koridorā.",
                    "preconditions": [
                        "Meteoroloģija atļauj ISR datu savākšanu"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Aizsargāt kabela koridoru",
                    "description": "Uzturēt patroles un integritātes uzraudzību pār atlikušo kabela maršrutu.",
                    "preconditions": [
                        "Patroles aktīvs var uzturēt staciju tuvumā no infrastruktūras"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinēt civilu gaisa telpu",
                    "description": "Noteikt provizoriskas procedūras ar civilās aviācijas aktoriem un izplatīt sensora signālus.",
                    "preconditions": [
                        "Civilās aviācijas iestāde ir pieejama"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Palielināt robežas uzraudzību",
                    "description": "Koordinēt uzraudzību un ziņošanu par konvoju tuvumā un pārsniegumiem.",
                    "preconditions": [
                        "Robežas patroles saikne ir pieejama"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinēt paketes gałęzes un dekonfliktēt retās resursus",
        "finish_to_start_condition": "Priekšējā uzdevums nodrošina nepieciešamo observācijas attēlu",
        "conditional_condition": "Escalate vēlāko paketes darbības tikai tad, ja uzraudzība apstiprina persistenci vai tuvošanos",
        "package_title": "Koordinēta pakete {titles}",
        "package_summary": "Sekvensēta padomes pakete ar uzdevumu atkarības, skaidru resursu rezervāciju un gałęžu koordināciju izvēlētajos COA."
    },
    "lt": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Įkurti šešėlio trasą",
                    "description": "Mokoti vizualaus/radaro kontakto saugio atstumoje ir pranešti apie modelio pokyčius.",
                    "preconditions": [
                        "Jūrų išsmoningas yra stacijoje"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Įdiegti ISR rinkimą",
                    "description": "Paleisti UAV ir prašyti palaikymo nuotoliniu jutimu virš operacinio koridoro.",
                    "preconditions": [
                        "Omingas leidžia ISR rinkimą"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Apsaugoti kabelio koridorą",
                    "description": "Mokoti patrolyje ir vientisumo stebėjime likusio kabelio maršchino virš.",
                    "preconditions": [
                        "Patrolyje išsmoningas gali išlaikyti staciją netoli infrastruktūros"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinuoti civilinį oro erdvę",
                    "description": "Nustatyti laikinas procedūras su civilinės aviacijos aktoriais ir padalinti jutimo ženklus.",
                    "preconditions": [
                        "Civilinės aviacijos įgamba pasiekiama"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Padidinti sienos stebėjimą",
                    "description": "Koordinuoti stebėjimą ir pranešimą apie konvojų prieigą ir pervažas.",
                    "preconditions": [
                        "Sienos patrolyje ryšys pasiekiamas"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinuoti paketo šakąs ir išspręsti trūkumą esančių išsmoningų",
        "finish_to_start_condition": "Anksčiau vykdomas darbas nustato reikiamą stebėjimo vaizdą",
        "conditional_condition": "Escalate vėlesnių paketo veiksmus tik jei stebėjimas patvirtina išlikimą ar artėjimą",
        "package_title": "Koordinuotas paketas {titles}",
        "package_summary": "Sekvencijuotas patarimų paketas su užduoties priklausomybėmis, aiškia išsmoningų rezervacija ir šakų koordinavimas pasirinktų COA tarpų."
    },
    "da": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Etabler skyggetrack",
                    "description": "Oprethold visuel/radar kontakt på sikker afstand og rapporter om mønsterændringer.",
                    "preconditions": [
                        "Maritim aktiv på station"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Udrul ISR-indsamling",
                    "description": "Lancér UAV og anmod om støttende fjernmåling over driftskorridoren.",
                    "preconditions": [
                        "Vejret tillader ISR-indsamling"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Beskyt kabelkorridor",
                    "description": "Oprethold patrulje og integritetsmonitorering over den resterende kabelrute.",
                    "preconditions": [
                        "Patruljeaktiv kan holde station nær infrastruktur"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordiner civil luftrum",
                    "description": "Fastlæg midlertidige procedurer med civile luftfartsdeltagere og distribuer sensorcues.",
                    "preconditions": [
                        "Civil luftfartsmyndighed er tilgængelig"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Øg grænseovervågning",
                    "description": "Koordiner overvågning og rapportering over konvojtilgange og krydsninger.",
                    "preconditions": [
                        "Grænsepatruljeforbindelse er tilgængelig"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordiner pakkegrene og afkonflikter knappe ressourcer",
        "finish_to_start_condition": "Forudgående opgave etablerer det nødvendige observationsbillede",
        "conditional_condition": "Eskaler senere pakkehandlinger kun hvis overvågning bekræfter vedholdenhed eller tilgang",
        "package_title": "Koordineret pakke for {titles}",
        "package_summary": "Sekventiel rådgivningspakke med opgaveafhængigheder, eksplicit reservering af aktiver og grenekoordinering på tværs af de valgte COA'er."
    },
    "no": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Etabler skyggetracking",
                    "description": "Oppretthold visuell/radar kontakt på trygg avstand og rapporter mønsterendringer.",
                    "preconditions": [
                        "Maritim ressurs på stasjon"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Utplassere ISR-innsamling",
                    "description": "Sende opp UAV og be om støttende fjernmåling over operasjonskorridoren.",
                    "preconditions": [
                        "Vær tillater ISR-innsamling"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Beskytte kabelkorridor",
                    "description": "Opprettholde patrulje og integritetsmonitorering over gjenværende kabelrute.",
                    "preconditions": [
                        "Patruljeressurs kan holde stasjon nær infrastruktur"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinere sivil luftrom",
                    "description": "Fastsette midlertidige prosedyrer med sivile luftfartsaktører og distribuere sensorkues.",
                    "preconditions": [
                        "Sivil luftfartsmyndighet er tilgjengelig"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Øke grenseovervåking",
                    "description": "Koordinere overvåking og rapportering over konvoi-tilnærminger og kryssinger.",
                    "preconditions": [
                        "Grensepatrulje-kontakt er tilgjengelig"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinere pakkegrener og avklare knappe ressurser",
        "finish_to_start_condition": "Forrige oppgave etablerer det nødvendige observasjonsbildet",
        "conditional_condition": "Eskaler senere pakkehandlinger kun hvis overvåking bekrefter vedvarenhet eller tilnærming",
        "package_title": "Koordinert pakke for {titles}",
        "package_summary": "Sekvensiell rådgivningspakke med oppgaveavhengigheter, eksplisitt ressursreservasjon og grenerkoordinering på tvers av de valgte COA-ene."
    },
    "is": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Setja skuggaflok",
                    "description": "Varðandi sýnilegt/radar samband á öruggri fjarlægð og skýrartölur breytinga.",
                    "preconditions": [
                        "Sjóferðarmiðill á staðnum"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Setja í gang ISR innsamling",
                    "description": "Setja upp UAV og beita aðstoðar fjarlægsinsarannsóknar yfir virksemihlutinn.",
                    "preconditions": [
                        "Veður leyfir ISR innsamling"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Verja keblahlutinn",
                    "description": "Varðandi og eftirlit á heilbrigði yfir eftirfarandi keblahlutinn.",
                    "preconditions": [
                        "Varðandi miðill getur haldið staðnum nálægt innviðum"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Samræma borgarflugumhlutinn",
                    "description": "Setja tímabundnar aðferðir með borgarflugumhlutum og greina sensorlegar merki.",
                    "preconditions": [
                        "Borgarflugumstjórn er aðgangsileg"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Auka eftirlit yfir ræðumhlutinn",
                    "description": "Samræma eftirlit og skýrartölur yfir nálgunum og kryssingu í fylkingum.",
                    "preconditions": [
                        "Samhengi yfir ræðumhlutinn er til stangra"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Samræma greinar pakka og fjarlægja óþarfa miðill",
        "finish_to_start_condition": "Fyrri uppgerðin stofnar þörfileg eftirlitsmynd",
        "conditional_condition": "Hæja seinni pakka aðgerðir eingöngu ef eftirlit staðfestir varanleika eða nálgun",
        "package_title": "Samræmd pakka fyrir {titles}",
        "package_summary": "Röðrænt ráðgjafapakka með uppgerðar afhengerðum, sérstökum miðillaboka og greinaskýrslu yfir valda COA."
    },
    "fi": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Asettaa varjontracking",
                    "description": "Ylläpidä visuaalista/radari-yhteyttä turvallisesta etäisyydestä ja raportoi kuvion muutoksista.",
                    "preconditions": [
                        "Merellinen omaisuus asemassa"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Käynnistä ISR-keruu",
                    "description": "Laukaisu UAV ja pyydä tukea etähavainnointia toiminta-alueella.",
                    "preconditions": [
                        "Sää sallii ISR-keruun"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Suojaa kaapelireitti",
                    "description": "Ylläpidä partiointia ja eheyden seurantaa jäljellä olevalla kaapelireitillä.",
                    "preconditions": [
                        "Partiointiohjelma pystyy pitämään aseman infrastruktuurin lähellä"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinoi siviiliilmatila",
                    "description": "Aseta väliaikaiset menettelyt siviiliilmailutoimijoiden kanssa ja jaa sensori-vihjeitä.",
                    "preconditions": [
                        "Siviiliilmailuviranomainen tavoitettavissa"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Lisää rajavalvontaa",
                    "description": "Koordinoi valvontaa ja raportointia konvoijien lähestymisissä ja ylityksissä.",
                    "preconditions": [
                        "Rajavalvontayhteydenotto saatavilla"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinoi paketin haarautumia ja poikittaiskonfliktit harvojen resurssien osalta",
        "finish_to_start_condition": "Edeltävä tehtävä luo vaaditun havainto-/kuva-kuvan",
        "conditional_condition": "Esikysy myöhemmän paketin toimenpiteet vain, jos valvonta vahvistaa jatkuvuuden tai lähestymisen",
        "package_title": "Koordinoitu paketti {titles}",
        "package_summary": "Järjestetty neuvontapaketti tehtäväriippuvuuksilla, selkeällä resurssivarauksella ja haarautumisen koordinoinnilla valittujen COA:iden yli."
    },
    "sv": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Etablera skuggspårning",
                    "description": "Bibehålla visuell/radar kontakt på säkert avstånd och rapportera mönsterförändringar.",
                    "preconditions": [
                        "Maritim tillgång på plats"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Utplacera ISR-insamling",
                    "description": "Starta UAV och begära stödjande fjärranalys över operationskorridoren.",
                    "preconditions": [
                        "Väder tillåter ISR-insamling"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Skydda kabelkorridoren",
                    "description": "Bibehålla patrull och integritetsövervakning över den återstående kabelrutten.",
                    "preconditions": [
                        "Patrulltillgång kan hålla position nära infrastruktur"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinera civil luftrum",
                    "description": "Sätta tillfälliga procedurer med civila luftfartsorganisationer och distribuera sensorkoder.",
                    "preconditions": [
                        "Civil luftfartsmyndighet nåbar"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Öka gränskontrollen",
                    "description": "Koordinera övervakning och rapportering vid konvojanslutningar och korsningar.",
                    "preconditions": [
                        "Gränspatrullskontakt tillgänglig"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinera paketgrenar och avkonfliktera knappa tillgångar",
        "finish_to_start_condition": "Föregående uppgift etablerar den nödvändiga observationsbilden",
        "conditional_condition": "Eskalera senare paketåtgärder endast om övervakningen bekräftar ihållande eller närmande",
        "package_title": "Koordinerat paket för {titles}",
        "package_summary": "Sekvenserat rådgivningspaket med uppgiftsberoenden, explicit tillgångsreservation och grenkoordinering över de valda COA:erna."
    },
    "sq": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Vendosni rrug (Shadow track)",
                    "description": "Mbani kontakt vizual/radar në distancë të sigurt dhe raportoni ndryshimet e modelit.",
                    "preconditions": [
                        "Asetin detar në stacion"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Vendosni mbledhjen ISR",
                    "description": "Lansoni UAV dhe kërkoni ndjeshmëri të mbështetur me largësi mbi korridorin operativ.",
                    "preconditions": [
                        "Klima lejon mbledhjen ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Mbrojtni korridorin e kabllos",
                    "description": "Mbani patrullim dhe monitorim integriteti mbi rrugën e mbetur të kabllos.",
                    "preconditions": [
                        "Asetin patrullimi mund të mbajë stacion pranë infrastrukturës"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinoni hapësirën ajrore civile",
                    "description": "Vendosni procedura të përkohshme me aktorë e aviacionit civil dhe shpërndani sinjalet e sensorëve.",
                    "preconditions": [
                        "Autoriteti i aviacionit civil është i arritshëm"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Rritni monitorimin e kufirit",
                    "description": "Koordinoni vigjilancën dhe raportimin mbi qasjet dhe kalimet e konvojit.",
                    "preconditions": [
                        "Liaisoni i patrullimit të kufirit është i disponueshëm"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinoni degët e paketës dhe dekonfliktoni asetet të rralla",
        "finish_to_start_condition": "Tasku i mëparshëm vendos imazhin e vëzhgimit të kërkuar",
        "conditional_condition": "Eskaloni veprimet e paketës më të vonë vetëm nëse monitorimi konfirmon qëndrueshmëri ose qasje",
        "package_title": "Paketa e koordinuar për {titles}",
        "package_summary": "Paketa e këshillimit e sekuestruar me varësitë e taskeve, rezervimin e aseteve të qarta dhe koordinimin e degëve nëpër COA-të e zgjedhura."
    },
    "mk": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Уста навејна следење",
                    "description": "Одржувај визуелен/радарски контакт на безбедна дистанца и известувај за промени во образот.",
                    "preconditions": [
                        "Морско средство на станица"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Разголемување ISR собирање",
                    "description": "Лаунчирај БАВ и побарај поддршка со далекусензиско надгледување над оперативниот коридор.",
                    "preconditions": [
                        "Времето овозможува ISR собирање"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Заштита на кабелскиот коридор",
                    "description": "Одржувај патрулирање и мониторинг на интегритетот низ преостанатиот кабелски пат.",
                    "preconditions": [
                        "Патрулирачкото средство може да задржи станица блиску до инфраструктурата"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Координирање на цивилното воздушна простор",
                    "description": "Постави временски процедури со цивилни воздухопловни актери и дистрибуира сензорски сигнали.",
                    "preconditions": [
                        "Цивилна воздухопловна управа достапна"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Поголемување на границите на надзор",
                    "description": "Координирај надзор и известување над пристапите и преминот на конвојот.",
                    "preconditions": [
                        "Достапна врска со границата"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Координирај гранки на пакетот и деконфликтирај ретки ресурси",
        "finish_to_start_condition": "Претходната задача го утврдува потребниот сличен поглед",
        "conditional_condition": "Ескалирај понатамошни активности на пакетот само ако надзорот потврди постојаност или приближување",
        "package_title": "Координиран пакет за {titles}",
        "package_summary": "Последна пакет со задатки со зависности на задачи, експлицитна резервација на ресурси и координација на гранките низ избраните COA."
    },
    "me": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Uspostiti senkovani trag",
                    "description": "Održavati vizuelni/radarski kontakt na sigurnoj udaljenosti i izvještavati o promjenama obrasca.",
                    "preconditions": [
                        "Morski aktiv na stanici"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Postaviti ISR prikupljanje",
                    "description": "Pokrenuti UAV i zatražiti podršku daljinskog snimanja nad operativnim koridorom.",
                    "preconditions": [
                        "Vrijeme dozvoljava ISR prikupljanje"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Zaštititi kabl koridor",
                    "description": "Održavati patrole i nadzor integriteta nad preostalim kablovskim rutama.",
                    "preconditions": [
                        "Patrolni aktiv može zadržati stanicu blizu infrastrukture"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Koordinirati civilno zračni prostor",
                    "description": "Postaviti privremene procedure sa civilnim avijacionim akterima i distribuirati senzorske signale.",
                    "preconditions": [
                        "Civilna avijaciona vlast dostupna"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Povećati nadzor granice",
                    "description": "Koordinirati nadzor i izvještavanje nad pristupima i prelazima konvoja.",
                    "preconditions": [
                        "Dostupan je kontakt za graničku patrolu"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Koordinirati grane paketa i dekonfliktirati oskudne resurse",
        "finish_to_start_condition": "Prethodni zadatak uspostavlja potrebnu sliku observacije",
        "conditional_condition": "Eskalirati akcije kasnijih paketa samo ako monitoring potvrdi upornost ili približavanje",
        "package_title": "Koordinisani paket za {titles}",
        "package_summary": "Sekvencirani savjetodavni paket sa zavisnostima zadataka, eksplicitnom rezervacijom resursa i koordinacijom grana kroz odabrane COA-e."
    },
    "el": {
        "tasks": {
            "COA-TPL-SHADOW": [
                {
                    "title": "Εκκαθάριση παρακολούθησης",
                    "description": "Διατήρηση οπτικής/ραντάρ επαφής σε ασφαλή απόσταση και αναφορά αλλαγών μοτίβου.",
                    "preconditions": [
                        "Θαλάσσιο περιουσιακό στοιχείο στην θέση"
                    ]
                }
            ],
            "COA-TPL-ISR": [
                {
                    "title": "Εφαρμογή συλλογής ISR",
                    "description": "Εκκίνηση UAV και αίτημα υποστηρικτικής遥感 πάνω από τον λειτουργικό διάδρομο.",
                    "preconditions": [
                        "Ο καιρός επιτρέπει τη συλλογή ISR"
                    ]
                }
            ],
            "COA-TPL-CABLE-PROTECT": [
                {
                    "title": "Προστασία καλωδίου",
                    "description": "Διατήρηση περιπολίας και παρακολούθησης ακεραιότητας πάνω από τη διαμένοντα διαδρομή του καλωδίου.",
                    "preconditions": [
                        "Το περιουσιακό στοιχείο περιπολίας μπορεί να διατηρήσει τη θέση κοντά στην υποδομή"
                    ]
                }
            ],
            "COA-TPL-AIRSPACE": [
                {
                    "title": "Συντονισμός αεροδιαστημικού χώρου",
                    "description": "Καθορισμός προσωρινών διαδικασιών με τους φορείς της πολιτικής αεροπορίας και διανομή σημάτων αισθητήρων.",
                    "preconditions": [
                        "Διαθέσιμη η αρχή πολιτικής αεροπορίας"
                    ]
                }
            ],
            "COA-TPL-BORDER": [
                {
                    "title": "Αύξηση παρακολούθησης των συνόρων",
                    "description": "Συντονισμός επιτήρησης και αναφοράς στις προσέρχομες και διέρχομες काफिलों.",
                    "preconditions": [
                        "Διαθέσιμη σύνδεση με την περιπολία των συνόρων"
                    ]
                }
            ]
        },
        "soft_sync_condition": "Συντονισμός κλάδων πακέτου και αποσυγκράτηση σπάνιων περιουσιακών στοιχείων",
        "finish_to_start_condition": "Η προηγούμενη εργασία καθιερώνει το απαιτούμενο εικόνα παρακολούθησης",
        "conditional_condition": "Εκβαθμισμός των ενεργειών του μεταγενέστερου πακέτου μόνο εάν η παρακολούθηση επιβεβαιώνει τη 지속τικότητα ή την προσέγγιση",
        "package_title": "Συντονισμένο πακέτο για {titles}",
        "package_summary": "Ακολουθούμενο πακέτο συμβουλών με εξαρτήσεις εργασιών, ρητή κράτηση περιουσιακών στοιχείων και συντονισμό κλάδων σε όλες τις επιλεγμένες COA."
    }
}
