from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import json
import os
import re
import sys
from urllib import request as urllib_request
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'arlo-goc-onboarding-secret-key-2024'

# Data structure for checklist items
CHECKLIST_ITEMS = {
    'pre_day1': [
        {'id': 'laptop', 'title': 'Laptop and equipment received', 'description': 'Ensure you have received your laptop, monitors, and accessories'},
        {'id': 'email', 'title': 'Outlook email account activated', 'description': 'Verify you can access your @arlo.com email'},
        {'id': 'vpn', 'title': 'VPN credentials received', 'description': 'Obtain VPN access credentials for remote work'},
    ],
    'week1': [
        {'id': 'jira', 'title': 'Jira access configured', 'description': 'Access to Arlo Jira instance with appropriate project permissions'},
        {'id': 'servicenow', 'title': 'ServiceNow account active', 'description': 'ServiceNow access for incident and change management'},
        {'id': 'pagerduty', 'title': 'PagerDuty profile setup', 'description': 'PagerDuty account with on-call schedule visibility'},
        {'id': 'ping', 'title': 'Ping Identity configured', 'description': 'Single Sign-On (SSO) access via Ping Identity'},
        {'id': 'slack', 'title': 'Slack workspace joined', 'description': 'Join #goc-team, #incidents, #alerts channels'},
        {'id': 'documentation', 'title': 'Documentation access', 'description': 'Confluence and internal wiki access'},
        {'id': 'training_day1', 'title': 'Complete Day 1 Training', 'description': 'GOC Overview and Introduction'},
        {'id': 'training_day2', 'title': 'Complete Day 2 Training', 'description': 'Monitoring Systems and Tools'},
        {'id': 'training_day3', 'title': 'Complete Day 3 Training', 'description': 'Incident Management Process'},
        {'id': 'training_day4', 'title': 'Complete Day 4 Training', 'description': 'Escalation Procedures and Communication'},
        {'id': 'training_day5', 'title': 'Complete Day 5 Training', 'description': 'Hands-on Practice and Review'},
    ],
    'week2': [
        {'id': 'shadowing', 'title': 'Shadow senior engineer', 'description': 'Complete 3 weeks shadowing sessions'},
        {'id': 'runbook', 'title': 'Review runbook procedures', 'description': 'Familiarize with common incident runbooks'}
        ]
}

# Training modules data
TRAINING_MODULES = {
    'day1': {
        'title': 'Day 1: Team Introduction & Operations',
        'topics': [
            {'name': 'Team Introduction & Project Overview', 'duration': '60 min', 'type': 'presentation'},
            {'name': 'Routine Activity: Alerting, Red Metrics Monitoring, Deployment Activities, Terraform', 'duration': '90 min', 'type': 'hands-on'},
            {'name': 'NOC SOPs (Standard Operating Procedures)', 'duration': '60 min', 'type': 'presentation'},
            {'name': 'Production Deployment Process', 'duration': '75 min', 'type': 'hands-on'},
            {'name': 'System Health Check after Production Deployment', 'duration': '45 min', 'type': 'hands-on'},
            {'name': 'Demo of the Scorecard Tool', 'duration': '30 min', 'type': 'demo'},
            {'name': 'War-room Process', 'duration': '45 min', 'type': 'presentation'},
            {'name': 'NOC SLA (Service Level Agreements)', 'duration': '30 min', 'type': 'presentation'},
        ],
        'objectives': [
            'Understand team structure and project overview',
            'Learn routine monitoring activities and deployment processes',
            'Master NOC standard operating procedures',
            'Understand production deployment and health check processes',
            'Learn war-room procedures and escalation protocols',
            'Understand NOC SLA and priority definitions'
        ],
        'resources': [
            'Volansys Team - Structure',
            'NOC Bible: https://arlo.atlassian.net/wiki/display/DOES/NOC+Bible',
            'Training Sessions: https://arlo.atlassian.net/wiki/display/DOES/Traning+Sessions+for+new+joiners',
            'NOC Team Process: https://acs.arlo.com/display/DOES/NOC+Team+Process+index',
            'System Health Check Guide',
            'Arlo Deployment Scorecard: https://scorecard.arlocloud.com/',
            'War Room Process: https://arlo.atlassian.net/wiki/pages/viewpage.action?pageId=55215297',
            'Bug Priority Definitions: https://arlo.atlassian.net/wiki/display/AQT/Bug+Priority+Definitions',
            'Zoom Recording - Day 1 (Passcode: ajdKkg7#)'
        ]
    },
    'day2': {
        'title': 'Day 2: Datadog & Monitoring Tools',
        'topics': [
            {'name': 'Datadog Tool Overview and Detail Walkthrough', 'duration': '90 min', 'type': 'hands-on'},
            {'name': 'Mandatory Dashboard Review', 'duration': '60 min', 'type': 'presentation'},
            {'name': 'PagerDuty Process to Initiate Escalation', 'duration': '60 min', 'type': 'hands-on'},
            {'name': 'NOC Ticket Creation Process (Tags, Labels, Priority)', 'duration': '60 min', 'type': 'hands-on'},
            {'name': 'Process of Alert Monitoring', 'duration': '45 min', 'type': 'presentation'},
            {'name': 'Alerts to be Ignored', 'duration': '30 min', 'type': 'discussion'},
            {'name': 'Excluded Endpoints in Monitoring Tools', 'duration': '30 min', 'type': 'presentation'},
        ],
        'objectives': [
            'Master Datadog tool navigation and usage',
            'Understand mandatory dashboard requirements',
            'Learn PagerDuty escalation procedures',
            'Create and manage NOC tickets with proper tags and labels',
            'Understand alert monitoring processes and exclusions',
            'Identify alerts to be ignored and excluded endpoints'
        ],
        'resources': [
            'Datadog Tool Documentation',
            'Mandatory Dashboard List',
            'Splunk Alerts: https://arlo.atlassian.net/wiki/display/DOES/Splunk+Alerts',
            'War Room Process: https://arlo.atlassian.net/wiki/pages/viewpage.action?pageId=55215297',
            'NOC Ticket Creation Guidelines',
            'Alerts to be Ignored: https://arlo.atlassian.net/wiki/display/DOES/NOC+Alerts+to+be+ignored',
            'Excluded Endpoints: https://arlo.atlassian.net/wiki/display/DOES/Excluded+Endpoints',
            'Zoom Recording - Day 2 (Passcode: 3G1L$%s^)'
        ]
    },
    'day3': {
        'title': 'Day 3: Alert Configuration & System Monitoring',
        'topics': [
            {'name': 'Alert and Dashboard Configuration Process (Datadog, Grafana, Splunk, CloudWatch)', 'duration': '90 min', 'type': 'hands-on'},
            {'name': 'Assets for Monitoring (Arlo BS/Camera details GDEV/PROD)', 'duration': '60 min', 'type': 'presentation'},
            {'name': 'Pingdom Monitoring URL List', 'duration': '45 min', 'type': 'hands-on'},
            {'name': 'Critical Metrics (status.arlo.com)', 'duration': '45 min', 'type': 'presentation'},
            {'name': 'System Health Check Process and Validation Post-Deployment', 'duration': '60 min', 'type': 'hands-on'},
            {'name': 'Version Page Overview', 'duration': '30 min', 'type': 'presentation'},
            {'name': 'Monthly and Weekly Reports', 'duration': '30 min', 'type': 'discussion'},
            {'name': 'Custom Scripts for xBroker, MQTT, Streaming, etc.', 'duration': '60 min', 'type': 'hands-on'},
            {'name': 'Dashboards and Splunk Query for Verisure Batch Processing', 'duration': '45 min', 'type': 'hands-on'},
        ],
        'objectives': [
            'Configure alerts and dashboards across multiple platforms',
            'Understand monitoring assets for Basestations and Cameras',
            'Learn Pingdom URL monitoring and critical metrics',
            'Master post-deployment health check procedures',
            'Understand custom scripts for xBroker, MQTT, and Streaming',
            'Work with Verisure batch processing dashboards and queries'
        ],
        'resources': [
            'Alert Configuration Guide (Datadog, Grafana, Splunk, CloudWatch)',
            'Arlo BS/Camera Details GDEV/PROD',
            'Pingdom Monitoring URL List: https://arlo.atlassian.net/wiki/display/DOES/Pingdom+Monitoring+URL+List+for+Production',
            'Arlo Status Page: https://status.arlo.com/',
            'Datadog Critical Metrics Dashboard',
            'System Health Check: https://arlo.atlassian.net/wiki/spaces/DOES/pages/55157418',
            'Version Page Documentation',
            'cvrsstreaming Python Scripts',
            'xBroker Script Details: https://arlo.atlassian.net/wiki/display/DOES/Xbroker+Script+Details',
            'MQTT Script: https://arlo.atlassian.net/wiki/pages/viewpage.action?pageId=55158632',
            'Verisure Batch Processing Splunk Query',
            'Zoom Recording - Day 3 (Passcode: s^%x9qTO)'
        ]
    },
    'day4': {
        'title': 'Day 4: Arlo Services Architecture & Access',
        'topics': [
            {'name': 'Overview of Arlo Services and Architecture', 'duration': '120 min', 'type': 'presentation'},
            {'name': 'Service Owners and Embedded Engineers for Respective Services', 'duration': '90 min', 'type': 'discussion'},
            {'name': 'Access and Credentials Management', 'duration': '75 min', 'type': 'hands-on'},
        ],
        'objectives': [
            'Understand Arlo\'s complete service architecture',
            'Identify service owners and embedded engineers for each service',
            'Learn access and credential management procedures',
            'Understand service dependencies and interactions',
            'Know who to contact for specific service issues'
        ],
        'resources': [
            'SRE & NOC Knowledge-base: https://arlo.atlassian.net/wiki/spaces/AFS/pages/79102023/SRE+NOC+Knowledge-base',
            'Arlo Services Architecture Diagram',
            'Service Owners List: https://arlo.atlassian.net/wiki/spaces/DOES/pages/55156845',
            'Embedded Engineers Contact Directory',
            'NOC Team On-Boarding Access Checklist',
            'Credentials Management Guide',
            'Service Dependencies Map'
        ]
    },
    'day5': {
        'title': 'Day 5: Hands-on Practice and Review',
        'topics': [
            {'name': 'Simulated Incident Exercises', 'duration': '120 min', 'type': 'simulation'},
            {'name': 'Runbook Walkthrough Sessions', 'duration': '90 min', 'type': 'hands-on'},
            {'name': 'Q&A with Senior Engineers', 'duration': '60 min', 'type': 'discussion'},
            {'name': 'Week 1 Review and Assessment', 'duration': '45 min', 'type': 'assessment'},
            {'name': 'Next Steps and Shadowing Plan', 'duration': '30 min', 'type': 'planning'},
        ],
        'objectives': [
            'Apply learned skills in realistic scenarios',
            'Execute common runbook procedures',
            'Clarify any remaining questions',
            'Prepare for shadowing and on-call duties'
        ],
        'resources': [
            'Incident Simulation Scenarios',
            'Complete Runbook Library',
            'Week 1 Assessment Quiz',
            'Shadowing Schedule'
        ]
    }
}

# Essential tools data
ESSENTIAL_TOOLS = {
    'jira': {
        'name': 'Jira',
        'description': 'Project and ticket management system for tracking work and incidents',
        'url': 'https://arlo.atlassian.net',
        'access_request': 'Request access through IT Service Desk',
        'key_features': [
            'Create and manage incident tickets',
            'Track project work and sprints',
            'Custom dashboards and filters',
            'Integration with ServiceNow and PagerDuty'
        ],
        'getting_started': [
            'Log in using Ping Identity SSO',
            'Join the GOC project workspace',
            'Configure personal dashboard',
            'Review ticket workflow and status definitions'
        ]
    },
    'servicenow': {
        'name': 'ServiceNow',
        'description': 'IT Service Management platform for incidents, changes, and problems',
        'url': 'https://arlo.service-now.com',
        'access_request': 'Provisioned automatically on Day 1',
        'key_features': [
            'Incident management and tracking',
            'Change request workflows',
            'Knowledge base articles',
            'Asset and configuration management'
        ],
        'getting_started': [
            'Access via Ping Identity SSO',
            'Complete ServiceNow basics training module',
            'Familiarize with incident form fields',
            'Review SLA and priority definitions'
        ]
    },
    'pagerduty': {
        'name': 'PagerDuty',
        'description': 'Incident response and on-call management platform',
        'url': 'https://arlo.pagerduty.com',
        'access_request': 'Manager will add you to the GOC schedule',
        'key_features': [
            'Real-time alert notifications',
            'On-call schedule management',
            'Escalation policies',
            'Mobile app for on-the-go response'
        ],
        'getting_started': [
            'Install PagerDuty mobile app',
            'Configure notification preferences',
            'Test alert delivery to your devices',
            'Review your on-call schedule'
        ]
    },
    'ping': {
        'name': 'Ping Identity',
        'description': 'Single Sign-On (SSO) provider for secure access to all applications',
        'url': 'https://sso.arlo.com',
        'access_request': 'Automatically configured with your employee account',
        'key_features': [
            'Single sign-on to all Arlo applications',
            'Multi-factor authentication (MFA)',
            'Password management',
            'Self-service account recovery'
        ],
        'getting_started': [
            'Set up MFA using authenticator app',
            'Save your recovery codes securely',
            'Test SSO login to all tools',
            'Configure security questions'
        ]
    },
    'outlook': {
        'name': 'Outlook',
        'description': 'Email and calendar platform for business communication',
        'url': 'https://outlook.office.com',
        'access_request': 'Activated on your first day',
        'key_features': [
            'Corporate email (@arlo.com)',
            'Calendar and meeting scheduling',
            'Shared mailboxes for team communication',
            'Integration with Teams and Slack'
        ],
        'getting_started': [
            'Configure email client on all devices',
            'Subscribe to GOC shared calendar',
            'Set up email signatures',
            'Join distribution lists: goc-team@arlo.com'
        ]
    },
    'slack': {
        'name': 'Slack',
        'description': 'Real-time messaging and collaboration platform',
        'url': 'https://arlo.slack.com',
        'access_request': 'Invitation sent to your email on Day 1',
        'key_features': [
            'Team channels and direct messaging',
            'Integration with monitoring tools',
            'File sharing and collaboration',
            'Custom notifications and workflows'
        ],
        'getting_started': [
            'Join key channels: #goc-team, #incidents, #alerts, #announcements',
            'Configure notification preferences',
            'Install Slack mobile app',
            'Set up status and availability indicators'
        ]
    }
}

RESOURCE_INDEX = [
    {
        'title': 'NOC Bible (Knowledge Base)',
        'description': 'Step-by-step procedures for common incidents and operational playbooks.',
        'url': 'https://arlo.atlassian.net/wiki/spaces/DOES/pages/55151026/NOC+Bible',
        'tags': ['runbook', 'incident', 'noc', 'knowledge base']
    },
    {
        'title': 'NOC KT Training Page',
        'description': 'Complete knowledge transfer documentation for onboarding.',
        'url': 'https://arlo.atlassian.net/wiki/spaces/DOES/pages/55187717/NOC+KT',
        'tags': ['training', 'kt', 'onboarding', 'documentation']
    },
    {
        'title': 'SRE & NOC Knowledge-base',
        'description': 'System architecture and service ownership references.',
        'url': 'https://arlo.atlassian.net/wiki/spaces/AFS/pages/79102023/SRE+NOC+Knowledge-base',
        'tags': ['architecture', 'sre', 'services', 'owners']
    },
    {
        'title': 'War Room Process',
        'description': 'Escalation and incident war-room communication process.',
        'url': 'https://arlo.atlassian.net/wiki/pages/viewpage.action?pageId=55215297',
        'tags': ['war room', 'escalation', 'incident', 'process']
    },
    {
        'title': 'Deployment Scorecard',
        'description': 'Track release and deployment quality signals.',
        'url': 'https://scorecard.arlocloud.com/',
        'tags': ['deployment', 'release', 'scorecard', 'monitoring']
    },
    {
        'title': 'NOC Onboarding Checklist',
        'description': 'Access and credentials checklist for new joiners.',
        'url': 'https://arlo.atlassian.net/wiki/spaces/DOES/pages/55156845',
        'tags': ['checklist', 'access', 'credentials', 'onboarding']
    },
    {
        'title': 'Red Metrics Monitoring',
        'description': 'Datadog dashboard for RED metrics monitoring.',
        'url': 'https://arlo.datadoghq.com/dashboard/mpd-2aw-sfe/red---metrics',
        'tags': ['datadog', 'red metrics', 'monitoring', 'dashboard']
    },
    {
        'title': 'PagerDuty',
        'description': 'Incident response and on-call coordination.',
        'url': 'https://arlo.pagerduty.com',
        'tags': ['pagerduty', 'on-call', 'incident', 'alert']
    },
    {
        'title': 'ServiceNow',
        'description': 'Ticketing, incident and change management platform.',
        'url': 'https://arlo.service-now.com',
        'tags': ['servicenow', 'ticket', 'incident', 'change']
    },
    {
        'title': 'Jira',
        'description': 'Project and issue tracking for GOC workflows.',
        'url': 'https://arlo.atlassian.net',
        'tags': ['jira', 'ticket', 'project', 'tracking']
    }
]


def _tokenize(text):
    return [t for t in re.split(r'[^a-z0-9]+', text.lower()) if len(t) > 1]


def _search_resources(topic, limit=4):
    topic_tokens = set(_tokenize(topic))
    if not topic_tokens:
        return []

    scored = []
    for resource in RESOURCE_INDEX:
        haystack = ' '.join([
            resource['title'],
            resource['description'],
            ' '.join(resource['tags'])
        ]).lower()
        haystack_tokens = set(_tokenize(haystack))
        overlap = topic_tokens.intersection(haystack_tokens)
        score = len(overlap)
        if score > 0:
            scored.append((score, resource))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def _mcp_resource_answer(topic):
    """
    Optional MCP hook.
    Configure MCP_RESOURCE_ENDPOINT to call your multi-agent-mcp service.
    Expected JSON response: {"answer": "...", "resources": [{"title":"...", "url":"..."}]}
    """
    endpoint = os.environ.get('MCP_RESOURCE_ENDPOINT')
    if not endpoint:
        return None

    payload = json.dumps({'topic': topic}).encode('utf-8')
    req = urllib_request.Request(
        endpoint,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib_request.urlopen(req, timeout=10) as response:
        body = response.read().decode('utf-8')
        data = json.loads(body)
        return {
            'answer': data.get('answer', ''),
            'resources': data.get('resources', []),
            'source': 'mcp'
        }


def _multi_agent_mcp_search(topic):
    project_path = os.environ.get(
        'MULTI_AGENT_MCP_PATH',
        '/Users/jgilmacias.c/Documents/GenAI/LLM_ChatBot_Llama3/multi-agent-mcp'
    )
    if not os.path.isdir(project_path):
        return None

    if project_path not in sys.path:
        sys.path.insert(0, project_path)

    try:
        from tools.confluence_tool import confluence_search
    except Exception as exc:
        print(f'Unable to import multi-agent-mcp confluence tool: {exc}')
        return None

    try:
        html_result = confluence_search(topic)
    except Exception as exc:
        print(f'multi-agent-mcp confluence search failed: {exc}')
        return None

    links = re.findall(
        r'<tr>\s*<td>(.*?)</td>\s*<td><a href="(.*?)"',
        html_result,
        flags=re.IGNORECASE | re.DOTALL
    )
    resources = []
    for raw_title, url in links[:5]:
        title = re.sub(r'<.*?>', '', raw_title).strip()
        resources.append({
            'title': title or 'Confluence Result',
            'description': 'Result from multi-agent-mcp Confluence search.',
            'url': url
        })

    plain_text = re.sub(r'<.*?>', ' ', html_result).strip()
    if resources:
        answer = f"I found {len(resources)} Confluence result(s) from multi-agent-mcp for '{topic}'."
    else:
        answer = plain_text[:240] if plain_text else f'No matches found for {topic}.'

    return {
        'answer': answer,
        'resources': resources,
        'source': 'multi-agent-mcp'
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/checklist')
def checklist():
    # Load saved progress if exists
    progress = session.get('checklist_progress', {})
    return render_template('checklist.html', 
                         checklist=CHECKLIST_ITEMS,
                         progress=progress)


@app.route('/checklist/update', methods=['POST'])
def update_checklist():
    item_id = request.form.get('item_id')
    checked = request.form.get('checked') == 'true'
    
    # Get or initialize progress
    progress = session.get('checklist_progress', {})
    progress[item_id] = checked
    session['checklist_progress'] = progress
    
    return {'success': True, 'item_id': item_id, 'checked': checked}


@app.route('/checklist/send-to-slack', methods=['POST'])
def send_to_slack():
    """Send checklist status to Slack channel"""
    try:
        # Get checklist data from request
        data = request.get_json()
        items = data.get('items', {})
        
        # Calculate statistics
        total_items = len(items)
        completed_items = sum(1 for checked in items.values() if checked)
        completion_percentage = int((completed_items / total_items) * 100) if total_items > 0 else 0
        
        # Get current user info (you can customize this)
        user_name = session.get('user_name', 'New GOC Engineer')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build detailed status by category
        def get_category_status(category_name, category_items):
            category_completed = sum(1 for item_id in category_items if items.get(item_id, False))
            category_total = len(category_items)
            return f"{category_name}: {category_completed}/{category_total}"
        
        pre_day1_status = get_category_status("Pre-Day 1", [item['id'] for item in CHECKLIST_ITEMS['pre_day1']])
        week1_status = get_category_status("Week 1", [item['id'] for item in CHECKLIST_ITEMS['week1']])
        week2_status = get_category_status("Week 2", [item['id'] for item in CHECKLIST_ITEMS['week2']])
        
        # Create Slack message
        slack_message = f"""
🎯 *GOC Onboarding Progress Update*

👤 *Engineer:* {user_name}
📅 *Date:* {timestamp}
📊 *Overall Progress:* {completed_items}/{total_items} items completed ({completion_percentage}%)

*Breakdown by Phase:*
• {pre_day1_status}
• {week1_status}
• {week2_status}

{'🎉 *Congratulations! All items completed!*' if completion_percentage == 100 else '💪 *Keep up the great work!*'}

_Sent from Arlo GOC Onboarding Portal_
"""
        
        # Try to send to Slack using webhook or SDK
        slack_token = os.environ.get('SLACK_BOT_TOKEN')
        slack_channel = 'GNVN9PFTM'  # The channel ID from the URL
        
        if slack_token:
            try:
                # Try to use Slack SDK if available
                from slack_sdk import WebClient
                from slack_sdk.errors import SlackApiError
                
                client = WebClient(token=slack_token)
                
                # Send message
                response = client.chat_postMessage(
                    channel=slack_channel,
                    text=slack_message,
                    unfurl_links=False,
                    unfurl_media=False
                )
                
                return jsonify({
                    'success': True,
                    'message': f'Status sent to Slack successfully! ({completion_percentage}% complete)'
                })
                
            except ImportError:
                # Slack SDK not installed
                return jsonify({
                    'success': False,
                    'message': 'Slack SDK not installed. Please install slack_sdk package.'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Slack API error: {str(e)}'
                })
        else:
            # No token configured - return message for testing
            return jsonify({
                'success': True,
                'message': f'Demo mode: Status would be sent to Slack ({completion_percentage}% complete). Configure SLACK_BOT_TOKEN to enable.',
                'preview': slack_message
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/tools')
def tools():
    return render_template('tools.html', tools=ESSENTIAL_TOOLS)


@app.route('/training')
def training():
    return render_template('training.html', modules=TRAINING_MODULES)


@app.route('/training/<day>')
def training_day(day):
    if day in TRAINING_MODULES:
        module = TRAINING_MODULES[day]
        return render_template('training_day.html', 
                             day=day, 
                             module=module)
    return redirect(url_for('training'))


@app.route('/resources')
def resources():
    return render_template('resources.html')


@app.route('/chatbot/resources', methods=['POST'])
def chatbot_resources():
    data = request.get_json(silent=True) or {}
    topic = (data.get('topic') or '').strip()

    if not topic:
        return jsonify({
            'success': False,
            'message': 'Please provide a topic to search.'
        }), 400

    try:
        mcp_result = _mcp_resource_answer(topic)
        if mcp_result:
            return jsonify({
                'success': True,
                'topic': topic,
                'answer': mcp_result['answer'],
                'resources': mcp_result['resources'],
                'source': mcp_result['source']
            })
    except Exception as exc:
        # Continue with local fallback if MCP integration is unavailable.
        print(f'MCP resource lookup failed: {exc}')

    multi_agent_result = _multi_agent_mcp_search(topic)
    if multi_agent_result:
        return jsonify({
            'success': True,
            'topic': topic,
            'answer': multi_agent_result['answer'],
            'resources': multi_agent_result['resources'],
            'source': multi_agent_result['source']
        })

    matches = _search_resources(topic)
    if not matches:
        return jsonify({
            'success': True,
            'topic': topic,
            'answer': 'No direct match found. Try keywords like: incident, war room, pagerduty, datadog, runbook.',
            'resources': [],
            'source': 'local'
        })

    answer = (
        f"I found {len(matches)} relevant resource(s) for '{topic}'. "
        'Start with the first one for the best match.'
    )
    return jsonify({
        'success': True,
        'topic': topic,
        'answer': answer,
        'resources': matches,
        'source': 'local'
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
