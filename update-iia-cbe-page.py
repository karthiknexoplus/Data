import re

def update_iia_cbe_page():
    """Update IIA Cbe page with Office Bearers and Members data"""
    
    # Read the current template
    with open('templates/iia_cbe.html', 'r') as f:
        content = f.read()
    
    # Replace the main content with the new structure
    old_content = '''        <!-- IIA Data Table -->
        <div class="data-section">
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>S.No</th>
                            <th>Association ID</th>
                            <th>Association Name</th>
                            <th>Location</th>
                            <th>Industry Type</th>
                            <th>Established</th>
                            <th>Contact</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for record in iia_data %}
                        <tr>
                            <td>{{ record[0] }}</td>
                            <td><span class="id-badge">{{ record[1] }}</span></td>
                            <td><strong>{{ record[2] }}</strong></td>
                            <td>{{ record[3] }}</td>
                            <td><span class="type-badge">{{ record[4] }}</span></td>
                            <td>{{ record[5] }}</td>
                            <td>{{ record[6] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>'''
    
    new_content = '''        <!-- IIA Cbe Navigation -->
        <div class="iia-nav-section">
            <div class="nav-buttons">
                <button id="officeBearersBtn" class="nav-btn active" onclick="showOfficeBearers()">
                    <i class="fas fa-users-cog"></i>
                    Office Bearers
                </button>
                <button id="membersBtn" class="nav-btn" onclick="showMembers()">
                    <i class="fas fa-users"></i>
                    Members
                </button>
            </div>
        </div>

        <!-- Office Bearers Section -->
        <div id="officeBearersSection" class="content-section">
            <div class="section-header">
                <h3><i class="fas fa-users-cog"></i> Office Bearers (2015 onwards)</h3>
            </div>
            
            <!-- Current Office Bearers -->
            <div class="office-bearers-current">
                <h4>Current Office Bearers</h4>
                <div class="bearers-grid">
                    <div class="bearer-card chairman">
                        <div class="bearer-title">Chairman</div>
                        <div class="bearer-name">Ar. V.ARAVINDAN</div>
                    </div>
                    <div class="bearer-card vice-chairman">
                        <div class="bearer-title">Vice Chairman</div>
                        <div class="bearer-name">Ar. C.PRABHAKAR</div>
                    </div>
                    <div class="bearer-card secretary">
                        <div class="bearer-title">Jt.Secretary</div>
                        <div class="bearer-name">Ar. S.JEYAKUMAR</div>
                    </div>
                    <div class="bearer-card secretary">
                        <div class="bearer-title">Jt.Secretary</div>
                        <div class="bearer-name">Ar. MOHAMMED ALI SHARIEFF</div>
                    </div>
                    <div class="bearer-card treasurer">
                        <div class="bearer-title">Treasurer</div>
                        <div class="bearer-name">Ar. P. MANOHARAN</div>
                    </div>
                    <div class="bearer-card past-chairman">
                        <div class="bearer-title">Imm. Past Chairman</div>
                        <div class="bearer-name">Ar. O.LAKSHMANAN</div>
                    </div>
                </div>
                
                <h4>Executive Committee Members</h4>
                <div class="executive-members">
                    <div class="member-item">Ar. R.VINOD</div>
                    <div class="member-item">Ar. S.DINESH ANAND</div>
                    <div class="member-item">Ar. ANJANEYSH</div>
                    <div class="member-item">Ar. S.KANNAN</div>
                    <div class="member-item">Ar. AASHISH RAICHURAA</div>
                    <div class="member-item">Ar. D.SENTHIL</div>
                </div>
            </div>

            <!-- Historical Office Bearers -->
            <div class="office-bearers-historical">
                <h4>Historical Office Bearers</h4>
                <div class="historical-timeline">
                    <div class="timeline-item">
                        <div class="year">2013-2015</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. O.LAKSHMANAN</div>
                            <div class="bearer">Vice Chairman: Ar.V.ARAVINDAN</div>
                            <div class="bearer">Jt.Secretary: Ar. ANJANEYSH</div>
                            <div class="bearer">Jt.Secretary: Ar. C.PRABHAKAR</div>
                            <div class="bearer">Treasurer: Ar. S.DINESH ANAND</div>
                            <div class="bearer">Imm. Past Chairman: Ar. P.ARUN PRASAD</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2011-2013</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. P.ARUN PRASAD</div>
                            <div class="bearer">Vice Chairman: Ar. SAI VIVEKANAND</div>
                            <div class="bearer">Jt.Secretary: Ar. KARUNAMBIKA KUMAR</div>
                            <div class="bearer">Jt.Secretary: Ar. A.SASI KUMAR</div>
                            <div class="bearer">Treasurer: Ar. VASANTH KUMAR</div>
                            <div class="bearer">Imm. Past Chairman: Ar. ARIVUDAI NAMBI</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2008-2011</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. ARIVUDAI NAMBI</div>
                            <div class="bearer">Vice Chairman: Ar. R.GEETHA RANI</div>
                            <div class="bearer">Jt.Secretary: Ar. SIDDARTH G.SANKAR</div>
                            <div class="bearer">Jt.Secretary: Ar. LATHAA CHANDRAN</div>
                            <div class="bearer">Treasurer: Ar. C.PRABHAKAR</div>
                            <div class="bearer">Imm. Past Chairman: Ar. M.BHUVANASUNDAR</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2006-2008</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. M.BHUVANASUNDAR</div>
                            <div class="bearer">Vice Chairman: Ar. P.ARUN PRASAD</div>
                            <div class="bearer">Jt.Secretary: Ar. S.JEYAKUMAR</div>
                            <div class="bearer">Jt.Secretary: Ar. O.LAKSHMANAN</div>
                            <div class="bearer">Treasurer: Ar. V.ARAVINDAN</div>
                            <div class="bearer">Imm. Past Chairman: Ar. GOPINATH ARUNACHALAM</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2004-2006</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. M.BHUVANASUNDAR</div>
                            <div class="bearer">Vice Chairman: Ar. ARIVUDAI NAMBI</div>
                            <div class="bearer">Jt.Secretary: Ar. SAI VIVEKANAND</div>
                            <div class="bearer">Jt.Secretary: Ar. S.PONRAJ</div>
                            <div class="bearer">Treasurer: Ar. MAMOOD RASHEED</div>
                            <div class="bearer">Imm. Past Chairman: Ar. GOPINATH ARUNACHALAM</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2002-2004</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. GOPINATH ARUNACHALAM</div>
                            <div class="bearer">Vice Chairman: Ar. M.DHARMALINGAM</div>
                            <div class="bearer">Jt.Secretary: Ar. ELZA JOSEPH</div>
                            <div class="bearer">Jt.Secretary: Ar. M.BHUVANASUNDAR</div>
                            <div class="bearer">Treasurer: Ar. P.ARUN PRASAD</div>
                            <div class="bearer">Imm. Past Chairman: Ar. PHILIP R.J. FOWLER</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">2000-2002</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. PHILIP R.J. FOWLER</div>
                            <div class="bearer">Vice Chairman: Ar. S.M.SYED YASEEN</div>
                            <div class="bearer">Secretary: Ar. SAI VIVEKANAND</div>
                            <div class="bearer">Treasurer: Ar. ARIVUDAI NAMBI</div>
                            <div class="bearer">Imm. Past Chairman: Ar. N.MOHANRAJ</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">1998-2000</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. N.MOHANRAJ</div>
                            <div class="bearer">Secretary: Ar. ELZA JOSEPH</div>
                            <div class="bearer">Treasurer: Ar. S.KARTHIKEYAN</div>
                            <div class="bearer">Imm. Past Chairman: Ar. BALAKRISHNAA VASUDEVAN</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">1995-1998</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. BALAKRISHNAA VASUDEVAN</div>
                            <div class="bearer">Secretary: Ar. ASHOK GOPALAKRISHNAN</div>
                            <div class="bearer">Treasurer: Ar. LAKSHMANAN OTHAMAN</div>
                            <div class="bearer">Imm. Past Chairman: Ar. RAJKUMAR DAVIDAR</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">1993-1995</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. RAJKUMAR DAVIDAR</div>
                            <div class="bearer">Secretary: Ar. PHILIP R.J.FOWLER</div>
                            <div class="bearer">Treasurer: Ar. RAVI NAIR</div>
                            <div class="bearer">Imm. Past Chairman: Ar. V.H.S.MONI</div>
                        </div>
                    </div>
                    
                    <div class="timeline-item">
                        <div class="year">1991-1993</div>
                        <div class="bearers">
                            <div class="bearer">Chairman: Ar. V.H.S.MONI</div>
                            <div class="bearer">Secretary: Ar. S.M.SYED YASEEN</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Members Section -->
        <div id="membersSection" class="content-section" style="display: none;">
            <div class="section-header">
                <h3><i class="fas fa-users"></i> IIA Coimbatore Members</h3>
            </div>
            
            <div class="members-grid">
                <div class="member-item">Ar.Aashish Raichuraa</div>
                <div class="member-item">Ar.Amutha Rajkumar</div>
                <div class="member-item">Ar. Anjaneysh Balakrishnaa</div>
                <div class="member-item">Ar. Aravindan . V</div>
                <div class="member-item">Ar. Arivudainambi.S</div>
                <div class="member-item">Ar. Arun Prasad</div>
                <div class="member-item">Ar. Ashok Gopalakrishnan</div>
                <div class="member-item">Ar. Balakrishnaa .V</div>
                <div class="member-item">Ar. Bhuvana Sundar</div>
                <div class="member-item">Ar. Dilip Kumar Joshi</div>
                <div class="member-item">Ar. Dinesh Anand . S</div>
                <div class="member-item">Ar. Dinesh Kumar .M</div>
                <div class="member-item">Ar. Dhandapani . P.A.</div>
                <div class="member-item">Ar. Dharmalingam . M</div>
                <div class="member-item">Ar. Geetha . K</div>
                <div class="member-item">Ar. Geetha Muthiah</div>
                <div class="member-item">Ar. Gokila Vijayalakshmi .S.D.</div>
                <div class="member-item">Ar. Gopinath Arunachalam*</div>
                <div class="member-item">Ar. Hari Baskar</div>
                <div class="member-item">Ar. Ilango . S.A.</div>
                <div class="member-item">Ar. Issac . A</div>
                <div class="member-item">Ar. Janardhanan . G</div>
                <div class="member-item">Ar. Jeyakumar</div>
                <div class="member-item">Ar. John Antony . JR</div>
                <div class="member-item">Ar. E.K.E. Joseph</div>
                <div class="member-item">Ar. Kalpana Jayakumar</div>
                <div class="member-item">Ar. Kalayana Sundaram</div>
                <div class="member-item">Ar. Karthick Arun</div>
                <div class="member-item">Ar. Karthikeyan . P</div>
                <div class="member-item">Ar. Karthikeyan . S</div>
                <div class="member-item">Ar. Karunambika Kumar</div>
                <div class="member-item">Ar. Kathiravan. P *</div>
                <div class="member-item">Ar. Krishnaraj . KV</div>
                <div class="member-item">Ar. Krisharajan . D</div>
                <div class="member-item">Ar. Krithika Jayabalan</div>
                <div class="member-item">Ar.Lakshmanan.O</div>
                <div class="member-item">Ar. Lathaa Chandran</div>
                <div class="member-item">Ar. Magesh Yoganand</div>
                <div class="member-item">Ar. Mamood Rashid</div>
                <div class="member-item">Ar. Mini Mariamma Thomas</div>
                <div class="member-item">Ar. Mohamed Aazam</div>
                <div class="member-item">Ar. Mohamed Ali Sheriff</div>
                <div class="member-item">Ar. Mohanraj . N</div>
                <div class="member-item">Ar. Moni V H S</div>
                <div class="member-item">Ar. Prabhakar.C</div>
                <div class="member-item">Ar. Ramani Sankar . T.S.</div>
                <div class="member-item">Ar. Swaminathan . G</div>
                <div class="member-item">Ar. Manoharan . P</div>
                <div class="member-item">Ar. Maruthachalam . M</div>
                <div class="member-item">Ar. Mohammad Hasim Ali</div>
                <div class="member-item">Ar. Nallasamy</div>
                <div class="member-item">Ar. Nanda Kumar . P</div>
                <div class="member-item">Ar. Philip. R.J. Fowler</div>
                <div class="member-item">Ar. Prabhu . D</div>
                <div class="member-item">Ar. Ponnuraj</div>
                <div class="member-item">Ar. Prabhakaran . C</div>
                <div class="member-item">Ar. Rajkumar N. Davidar</div>
                <div class="member-item">Ar. Ramakrishnamurthy</div>
                <div class="member-item">Ar. Rekha Srinivasan</div>
                <div class="member-item">Ar. Rajkumar . D</div>
                <div class="member-item">Ar. Shrinee Raichuraa</div>
                <div class="member-item">Ar. Sivaramkumar</div>
                <div class="member-item">Ar. Shashikala . S. Iyer</div>
                <div class="member-item">Ar. Subramani Kubendran</div>
                <div class="member-item">Ar. Suresh Sundrama Kumar</div>
                <div class="member-item">Ar. Sai Vivek</div>
                <div class="member-item">Ar. Sridhar . P.S.</div>
                <div class="member-item">Ar. Sasi Kumar . A</div>
                <div class="member-item">Ar. Siva Kumar . R</div>
                <div class="member-item">Ar. Siva . S</div>
                <div class="member-item">Ar. Shilpa Dugar</div>
                <div class="member-item">Ar. Syed Yaseen . S.M.</div>
                <div class="member-item">Ar. Siddharth Sankar</div>
                <div class="member-item">Ar. Senthil Duraisamy</div>
                <div class="member-item">Ar. Sivaraj . N</div>
                <div class="member-item">Ar. Sampigethaya Shama</div>
                <div class="member-item">Ar. Varghese Thomas</div>
                <div class="member-item">Ar. Vidyalatha</div>
                <div class="member-item">Ar. Vasantha Kumar</div>
                <div class="member-item">Ar. Vivit Samuel Vedaraj</div>
                <div class="member-item">Ar. Vijay Anand</div>
                <div class="member-item">Ar. Vinod . R</div>
                <div class="member-item">Ar. Aravind . S.P.</div>
                <div class="member-item">Ar. Charles Raja</div>
                <div class="member-item">Ar. Gandeepan</div>
                <div class="member-item">Ar. Kamalahasan Ramaswamy</div>
                <div class="member-item">Ar. Kannan . S</div>
                <div class="member-item">Ar. Lakshmi . S.V</div>
                <div class="member-item">Ar. Manikandan Ilango</div>
                <div class="member-item">Ar. Manimaran</div>
                <div class="member-item">Ar. Mohanraj . A</div>
                <div class="member-item">Ar. Nalini . S</div>
                <div class="member-item">Ar. Prasanna Parvatikar</div>
                <div class="member-item">Ar. Prabhu Manivannan</div>
                <div class="member-item">Ar. Preston Varghese</div>
                <div class="member-item">Ar. Paul</div>
                <div class="member-item">Ar. Rajagopalan. K</div>
                <div class="member-item">Ar. Ragavendran . P</div>
                <div class="member-item">Ar. Rukmani Karthic</div>
                <div class="member-item">Ar. Roopashree Parvatikar</div>
                <div class="member-item">Ar. Ramakrishnan . R.P.</div>
                <div class="member-item">Ar. Ramesh .</div>
                <div class="member-item">Ar. Sadiq Moosa</div>
                <div class="member-item">Ar. Shakunthala</div>
                <div class="member-item">Ar. Shiva Chandhran . S</div>
                <div class="member-item">Ar. Vijaya . P</div>
                <div class="member-item">Ar. Vishnu Vardhan</div>
                <div class="member-item">Ar.Karthick V</div>
                <div class="member-item">Ar.jeyakumar.s</div>
                <div class="member-item">Ar.Biswajit Paul</div>
            </div>
        </div>'''
    
    content = content.replace(old_content, new_content)
    
    # Add JavaScript for navigation
    js_code = '''
    <script>
    function showOfficeBearers() {
        document.getElementById('officeBearersSection').style.display = 'block';
        document.getElementById('membersSection').style.display = 'none';
        document.getElementById('officeBearersBtn').classList.add('active');
        document.getElementById('membersBtn').classList.remove('active');
    }
    
    function showMembers() {
        document.getElementById('officeBearersSection').style.display = 'none';
        document.getElementById('membersSection').style.display = 'block';
        document.getElementById('membersBtn').classList.add('active');
        document.getElementById('officeBearersBtn').classList.remove('active');
    }
    </script>'''
    
    # Add the JavaScript before the closing body tag
    content = content.replace('</body>', js_code + '</body>')
    
    # Write the updated content
    with open('templates/iia_cbe.html', 'w') as f:
        f.write(content)
    
    print("✅ Updated IIA Cbe page with Office Bearers and Members!")

if __name__ == "__main__":
    update_iia_cbe_page()
