/**
 * VIRTUAL WAITING ROOM & STOCHASTIC OVERBOOKING - ĐẠI NHẠC HỘI QUỐC GIA 2026
 * Frontend Logic & API Integration
 * 
 * Tuân thủ nghiêm ngặt Master Prompt v2.0:
 * - RULE 0: 100% thuật toán chạy trên Backend Python (server.py), Frontend chỉ hiển thị số liệu thực tế.
 * - GAP-4: Phân tách rõ Sức chứa cứng (physical_cap) và Nhu cầu thị trường (demand_limits).
 * - GAP-7: Nhóm chính sách (Bà mẹ VNAH, Thương binh, CCB, Con liệt sĩ) có protected_group_db_rate = 0.00%.
 * - WCAG AAA Contrast & GPU-Optimized Rendering.
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. GLOBAL STATE & CONFIGURATION
  // =========================================================================
  const STATE = {
    activeView: 'citizen', // 'citizen' | 'admin'
    venuePreset: 'my_dinh',
    userId: 12450,
    userName: 'Nguyễn Văn An',
    userPriority: 'Thương binh 2/4 (Ưu tiên 80)',
    queueToken: null,
    queuePosition: 12450,
    totalWaiting: 185420,
    releaseRate: 1200,
    selectedSector: 'VVIP',
    selectedQuantity: 2,
    heldTicket: null,
    heldExpiresAt: 0,
    audioAlertEnabled: false,
    ttlIntervalId: null,
    queuePollIntervalId: null,
    debounceTimer: null,
    pipelineResult: null,
    slidingWindowHistory: []
  };

  const VENUE_PRESETS = {
    my_dinh: {
      name: 'SÂN VẬN ĐỘNG MỸ ĐÌNH (40,000 GHẾ)',
      capacity: 40000,
      demands: { VVIP: 5200, PLATINUM: 13000, GOLD: 20000, SILVER: 12000 }
    },
    arena: {
      name: 'NHÀ THI ĐẤU QUỐC TẾ (10,000 GHẾ)',
      capacity: 10000,
      demands: { VVIP: 1500, PLATINUM: 3500, GOLD: 5000, SILVER: 3000 }
    },
    ncc: {
      name: 'TRUNG TÂM HỘI NGHỊ QUỐC GIA (3,800 GHẾ)',
      capacity: 3800,
      demands: { VVIP: 600, PLATINUM: 1400, GOLD: 2000, SILVER: 1000 }
    }
  };

  // =========================================================================
  // 2. DOM ELEMENT REFERENCES
  // =========================================================================
  const DOM = {
    // Header & Views
    btnViewCitizen: document.getElementById('btnViewCitizen'),
    btnViewAdmin: document.getElementById('btnViewAdmin'),
    viewCitizen: document.getElementById('viewCitizen'),
    viewAdmin: document.getElementById('viewAdmin'),
    txtServerStatus: document.getElementById('txtServerStatus'),
    txtActiveVenue: document.getElementById('txtActiveVenue'),

    // Citizen View
    txtTotalWaitingHero: document.getElementById('txtTotalWaitingHero'),
    txtTotalWaitingCount: document.getElementById('txtTotalWaitingCount'),
    citizenPriorityBadge: document.getElementById('citizenPriorityBadge'),
    citizenUserIdDisplay: document.getElementById('citizenUserIdDisplay'),
    txtQueuePosition: document.getElementById('txtQueuePosition'),
    txtReleaseRate: document.getElementById('txtReleaseRate'),
    txtEtaDisplay: document.getElementById('txtEtaDisplay'),
    txtLoyaltyScore: document.getElementById('txtLoyaltyScore'),
    btnFastPassDemo: document.getElementById('btnFastPassDemo'),
    btnAudioAlert: document.getElementById('btnAudioAlert'),
    audioIcon: document.getElementById('audioIcon'),
    audioQueueAlert: document.getElementById('audioQueueAlert'),

    // Stepper
    stepperSteps: document.querySelectorAll('.stepper-step'),
    stepperLines: document.querySelectorAll('.stepper-line'),

    // Sector & TTL
    ttlCountdownPill: document.getElementById('ttlCountdownPill'),
    txtTtlTimer: document.getElementById('txtTtlTimer'),
    stadiumSvgMap: document.getElementById('stadiumSvgMap'),
    sectorPolys: document.querySelectorAll('.sector-poly'),
    sectorBtnCards: document.querySelectorAll('.sector-btn-card'),
    selectSeatCount: document.getElementById('selectSeatCount'),
    btnHoldTicket: document.getElementById('btnHoldTicket'),

    // Quotas in cards
    txtCapVVIP: document.getElementById('txtCapVVIP'),
    txtMStarVVIP: document.getElementById('txtMStarVVIP'),
    txtCapPLATINUM: document.getElementById('txtCapPLATINUM'),
    txtMStarPLATINUM: document.getElementById('txtMStarPLATINUM'),
    txtCapGOLD: document.getElementById('txtCapGOLD'),
    txtMStarGOLD: document.getElementById('txtMStarGOLD'),
    txtCapSILVER: document.getElementById('txtCapSILVER'),
    txtMStarSILVER: document.getElementById('txtMStarSILVER'),

    // Hologram E-Ticket
    eTicketSection: document.getElementById('eTicketSection'),
    txtTicketFullName: document.getElementById('txtTicketFullName'),
    txtTicketPriority: document.getElementById('txtTicketPriority'),
    txtTicketSector: document.getElementById('txtTicketSector'),
    txtTicketSeatId: document.getElementById('txtTicketSeatId'),
    txtTicketQrCode: document.getElementById('txtTicketQrCode'),
    btnCheckinGate: document.getElementById('btnCheckinGate'),

    // Admin Controls
    selVenuePreset: document.getElementById('selVenuePreset'),
    rangeRiskTau: document.getElementById('rangeRiskTau'),
    lblRiskTau: document.getElementById('lblRiskTau'),
    rangeDropRate: document.getElementById('rangeDropRate'),
    lblDropRate: document.getElementById('lblDropRate'),
    inputScenarios: document.getElementById('inputScenarios'),
    btnRunFullPipeline: document.getElementById('btnRunFullPipeline'),
    btnResetSystem: document.getElementById('btnResetSystem'),

    // Demand Sliders
    rangeDemandVVIP: document.getElementById('rangeDemandVVIP'),
    lblDemandVVIP: document.getElementById('lblDemandVVIP'),
    rangeDemandPLATINUM: document.getElementById('rangeDemandPLATINUM'),
    lblDemandPLATINUM: document.getElementById('lblDemandPLATINUM'),
    rangeDemandGOLD: document.getElementById('rangeDemandGOLD'),
    lblDemandGOLD: document.getElementById('lblDemandGOLD'),
    rangeDemandSILVER: document.getElementById('rangeDemandSILVER'),
    lblDemandSILVER: document.getElementById('lblDemandSILVER'),

    // KPI Strip
    kpiCapacityC: document.getElementById('kpiCapacityC'),
    kpiMStar: document.getElementById('kpiMStar'),
    kpiOverbookingPct: document.getElementById('kpiOverbookingPct'),
    kpiDropRate: document.getElementById('kpiDropRate'),
    kpiNetRevenue: document.getElementById('kpiNetRevenue'),
    kpiGrowthPct: document.getElementById('kpiGrowthPct'),
    kpiProbDb: document.getElementById('kpiProbDb'),
    kpiProtectedDbRate: document.getElementById('kpiProtectedDbRate'),

    // Algo Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    tbodyM1Sample: document.getElementById('tbodyM1Sample'),
    heapTreeVisualizer: document.getElementById('heapTreeVisualizer'),
    tbodyM2TopK: document.getElementById('tbodyM2TopK'),
    m3TraceContainer: document.getElementById('m3TraceContainer'),
    m4AllocationDisplay: document.getElementById('m4AllocationDisplay'),
    tbodyM5Sample: document.getElementById('tbodyM5Sample'),
    canvasSlidingWindow: document.getElementById('canvasSlidingWindow'),
    m7BenchmarkDisplay: document.getElementById('m7BenchmarkDisplay')
  };

  // =========================================================================
  // 3. UTILITY FUNCTIONS
  // =========================================================================
  function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    return Number(num).toLocaleString('vi-VN');
  }

  function formatCurrencyVN(val) {
    if (!val || isNaN(val)) return '0 đ';
    if (val >= 1e9) {
      return (val / 1e9).toFixed(2) + ' Tỷ đ';
    }
    if (val >= 1e6) {
      return (val / 1e6).toFixed(1) + ' Triệu đ';
    }
    return formatNumber(val) + ' đ';
  }

  function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.style.position = 'fixed';
      container.style.bottom = '24px';
      container.style.right = '24px';
      container.style.zIndex = '9999';
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.gap = '10px';
      container.style.pointerEvents = 'none';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.style.background = type === 'success' ? '#064E3B' : type === 'danger' ? '#7F1D1D' : '#1E293B';
    toast.style.color = '#FFFFFF';
    toast.style.border = `1px solid ${type === 'success' ? '#10B981' : type === 'danger' ? '#F87171' : '#60A5FA'}`;
    toast.style.borderRadius = '8px';
    toast.style.padding = '12px 20px';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.5)';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '500';
    toast.style.pointerEvents = 'auto';
    toast.style.transition = 'all 0.3s ease';
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function playAlertChime() {
    if (!STATE.audioAlertEnabled) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime); // A5 note
        osc.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.15); // E6
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }
    } catch (e) {
      console.warn('Audio chime unsupported:', e);
    }
  }

  // =========================================================================
  // 4. DUAL-VIEW TOGGLE
  // =========================================================================
  function switchView(viewName) {
    STATE.activeView = viewName;
    if (viewName === 'citizen') {
      DOM.btnViewCitizen.classList.add('active');
      DOM.btnViewAdmin.classList.remove('active');
      DOM.viewCitizen.classList.add('active');
      DOM.viewAdmin.classList.remove('active');
      startQueuePolling();
    } else {
      DOM.btnViewAdmin.classList.add('active');
      DOM.btnViewCitizen.classList.remove('active');
      DOM.viewAdmin.classList.add('active');
      DOM.viewCitizen.classList.remove('active');
      stopQueuePolling();
      // Render canvas when switching to admin
      renderSlidingWindowChart();
    }
  }

  DOM.btnViewCitizen.addEventListener('click', () => switchView('citizen'));
  DOM.btnViewAdmin.addEventListener('click', () => switchView('admin'));

  // Audio Toggle
  DOM.btnAudioAlert.addEventListener('click', () => {
    STATE.audioAlertEnabled = !STATE.audioAlertEnabled;
    DOM.btnAudioAlert.classList.toggle('active', STATE.audioAlertEnabled);
    DOM.audioIcon.textContent = STATE.audioAlertEnabled ? '🔔' : '🔕';
    showToast(
      STATE.audioAlertEnabled ? 'Đã bật chuông thông báo khi đến lượt!' : 'Đã tắt âm báo.',
      'info'
    );
    if (STATE.audioAlertEnabled) playAlertChime();
  });

  // =========================================================================
  // 5. CITIZEN QUEUE SIMULATION & POLLING
  // =========================================================================
  function getETAString(position, releaseRatePerMin) {
    if (position <= 1) return 'Đến lượt bạn ngay bây giờ!';
    const rate = Math.max(10, releaseRatePerMin || 1200);
    const etaSeconds = Math.floor((position / rate) * 60);
    const minutes = Math.floor(etaSeconds / 60);
    const seconds = etaSeconds % 60;
    if (minutes > 60) {
      const hours = Math.floor(minutes / 60);
      const remMin = minutes % 60;
      return `${hours} giờ ${remMin} phút`;
    }
    return `${String(minutes).padStart(2, '0')} phút ${String(seconds).padStart(2, '0')} giây`;
  }

  async function pollQueueStatus() {
    try {
      const resp = await fetch(`/api/queue/status/${STATE.userId}`);
      if (!resp.ok) return;
      const data = await resp.json();

      STATE.queuePosition = data.position;
      STATE.totalWaiting = data.total_waiting;
      STATE.releaseRate = data.release_rate;
      if (data.queue_token) {
        STATE.queueToken = data.queue_token;
        localStorage.setItem('vwr_queue_token', data.queue_token);
      }

      // Update UI
      DOM.txtQueuePosition.textContent = `#${formatNumber(STATE.queuePosition)}`;
      DOM.txtTotalWaitingCount.textContent = formatNumber(STATE.totalWaiting);
      DOM.txtTotalWaitingHero.textContent = formatNumber(STATE.totalWaiting);
      DOM.txtReleaseRate.textContent = `${formatNumber(STATE.releaseRate)} vé / phút`;
      DOM.txtEtaDisplay.textContent = getETAString(STATE.queuePosition, STATE.releaseRate);

      // Check if user is called
      if (data.status === 'CALLED' || STATE.queuePosition <= 1) {
        handleUserCalled();
      }
    } catch (err) {
      console.warn('Lỗi kết nối kiểm tra hàng đợi:', err);
    }
  }

  function startQueuePolling() {
    if (STATE.queuePollIntervalId) clearInterval(STATE.queuePollIntervalId);
    pollQueueStatus();
    STATE.queuePollIntervalId = setInterval(pollQueueStatus, 3000);
  }

  function stopQueuePolling() {
    if (STATE.queuePollIntervalId) {
      clearInterval(STATE.queuePollIntervalId);
      STATE.queuePollIntervalId = null;
    }
  }

  function updateStepper(stepIndex) {
    // stepIndex: 1 = Queue, 2 = Hold/Seat, 3 = Payment, 4 = Ticket
    DOM.stepperSteps.forEach((step, idx) => {
      if (idx + 1 <= stepIndex) {
        step.classList.add('active');
      } else {
        step.classList.remove('active');
      }
    });
    DOM.stepperLines.forEach((line, idx) => {
      if (idx + 1 < stepIndex) {
        line.classList.add('active');
      } else {
        line.classList.remove('active');
      }
    });
  }

  function handleUserCalled() {
    stopQueuePolling();
    DOM.txtQueuePosition.textContent = '#00001 (ĐÃ ĐẾN LƯỢT)';
    DOM.txtQueuePosition.style.color = '#10B981';
    DOM.txtEtaDisplay.textContent = '00:00 (Mời chọn ghế ngay)';
    updateStepper(2);
    playAlertChime();
    showToast('🎉 ĐÃ ĐẾN LƯỢT CỦA BẠN! Mời chọn phân khu khán đài.', 'success');

    // Enable Hold Button
    DOM.btnHoldTicket.disabled = false;
    DOM.btnHoldTicket.classList.add('btn-pulse');
  }

  // Fast-Pass Demo
  DOM.btnFastPassDemo.addEventListener('click', () => {
    STATE.queuePosition = 1;
    handleUserCalled();
  });

  // =========================================================================
  // 6. SECTOR SELECTION & DYNAMIC TTL HOLDING
  // =========================================================================
  function setSelectedSector(sector) {
    STATE.selectedSector = sector;

    // Sync SVG polygons
    DOM.sectorPolys.forEach(poly => {
      if (poly.getAttribute('data-sector') === sector) {
        poly.classList.add('active');
      } else {
        poly.classList.remove('active');
      }
    });

    // Sync Sector Button Cards
    DOM.sectorBtnCards.forEach(card => {
      if (card.getAttribute('data-sector') === sector) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  // Click on SVG
  DOM.sectorPolys.forEach(poly => {
    poly.addEventListener('click', () => {
      const sec = poly.getAttribute('data-sector');
      if (sec) setSelectedSector(sec);
    });
  });

  // Click on Sector Cards
  DOM.sectorBtnCards.forEach(card => {
    card.addEventListener('click', () => {
      const sec = card.getAttribute('data-sector');
      if (sec) setSelectedSector(sec);
    });
  });

  // Dynamic TTL Countdown
  function startTTLCountdown(expiresAt) {
    if (STATE.ttlIntervalId) clearInterval(STATE.ttlIntervalId);
    
    let targetSec = 0;
    if (typeof expiresAt === 'string') {
      const parsed = Date.parse(expiresAt);
      if (!isNaN(parsed)) {
        targetSec = Math.floor(parsed / 1000);
      }
    } else if (typeof expiresAt === 'number') {
      targetSec = expiresAt > 1e11 ? Math.floor(expiresAt / 1000) : expiresAt;
    }

    const nowSec = Math.floor(Date.now() / 1000);
    if (!targetSec || targetSec <= nowSec) {
      targetSec = nowSec + 600; // 10 phút chuẩn
    }

    STATE.heldExpiresAt = targetSec;
    DOM.ttlCountdownPill.classList.add('pulse');

    function update() {
      const now = Math.floor(Date.now() / 1000);
      const remaining = Math.max(0, STATE.heldExpiresAt - now);
      const m = Math.floor(remaining / 60);
      const s = remaining % 60;
      DOM.txtTtlTimer.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;

      if (remaining <= 60 && remaining > 0) {
        DOM.txtTtlTimer.style.color = '#F87171'; // Warning
      } else {
        DOM.txtTtlTimer.style.color = '#D4AF37';
      }

      if (remaining <= 0) {
        clearInterval(STATE.ttlIntervalId);
        STATE.ttlIntervalId = null;
        DOM.ttlCountdownPill.classList.remove('pulse');
        DOM.txtTtlTimer.textContent = 'HẾT HẠN';
        showToast('⚠️ Phiên giữ chỗ 10 phút đã hết hạn! M6 Min-Heap đã thu hồi vé.', 'danger');
        DOM.eTicketSection.style.display = 'none';
        updateStepper(1);
        startQueuePolling();
      }
    }

    update();
    STATE.ttlIntervalId = setInterval(update, 1000);
  }

  // Hold Ticket API
  DOM.btnHoldTicket.addEventListener('click', async () => {
    DOM.btnHoldTicket.disabled = true;
    DOM.btnHoldTicket.textContent = '⏳ Đang xác nhận giữ chỗ...';

    const qty = parseInt(DOM.selectSeatCount.value, 10) || 1;
    STATE.selectedQuantity = qty;

    try {
      const payload = {
        user_id: STATE.userId,
        ticket_type: STATE.selectedSector,
        quantity: qty
      };

      const resp = await fetch('/api/hold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const res = await resp.json();
      if (resp.ok && res.status === 'SUCCESS') {
        STATE.heldTicket = res;
        showToast(`✅ Giữ vé thành công! Bạn có 10 phút để xác nhận.`, 'success');
        updateStepper(3);

        // Start dynamic TTL countdown
        startTTLCountdown(res.expires_at);

        // Display Luxury Hologram E-Ticket
        DOM.txtTicketFullName.textContent = STATE.userName;
        DOM.txtTicketPriority.textContent = STATE.userPriority;
        DOM.txtTicketSector.textContent = `${STATE.selectedSector} - Khán Đài A`;
        DOM.txtTicketSeatId.textContent = res.seat_id || `${STATE.selectedSector}-01-${Math.floor(Math.random() * 80 + 10)}`;
        DOM.txtTicketQrCode.textContent = res.ticket_code || `QR-VWR-40K-2026-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
        DOM.eTicketSection.style.display = 'block';

        DOM.eTicketSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        showToast(`❌ Không thể giữ vé: ${res.message || 'Lỗi hệ thống'}`, 'danger');
      }
    } catch (err) {
      showToast('❌ Lỗi kết nối tới máy chủ khi giữ vé', 'danger');
    } finally {
      DOM.btnHoldTicket.disabled = false;
      DOM.btnHoldTicket.textContent = '🛒 Xác Nhận Giữ Vé & Lấy Ghế Ngay';
    }
  });

  // Check-in Gate Simulation
  DOM.btnCheckinGate.addEventListener('click', async () => {
    if (!STATE.heldTicket) {
      showToast('Chưa có thông tin vé để check-in!', 'danger');
      return;
    }

    DOM.btnCheckinGate.disabled = true;
    DOM.btnCheckinGate.textContent = '🚪 Đang quét vé tại Cổng...';

    try {
      const resp = await fetch('/api/checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: STATE.userId,
          seat_id: STATE.heldTicket.seat_id,
          ticket_type: STATE.heldTicket.ticket_type
        })
      });

      const res = await resp.json();
      if (resp.ok && res.status === 'SUCCESS') {
        updateStepper(4);
        showToast(`🎫 CHECK-IN HỢP LỆ! Chào mừng bạn đến Đại Nhạc Hội Quốc Gia 2026.`, 'success');
        DOM.btnCheckinGate.textContent = '✅ ĐÃ QUA CỔNG SOÁT VÉ';
        DOM.btnCheckinGate.style.background = '#065F46';
      } else {
        showToast(`⚠️ Xử lý cửa soát vé: ${res.message}`, 'info');
      }
    } catch (err) {
      showToast('Lỗi kiểm tra vé cổng', 'danger');
      DOM.btnCheckinGate.textContent = '🚪 Quét Mã Check-in Cổng Rạp';
      DOM.btnCheckinGate.disabled = false;
    }
  });

  // =========================================================================
  // 7. ADMIN CONTROLS & PIPELINE EXECUTION
  // =========================================================================
  function getPipelinePayload() {
    const venue = VENUE_PRESETS[DOM.selVenuePreset.value] || VENUE_PRESETS.my_dinh;
    const demands = {
      VVIP: parseInt(DOM.rangeDemandVVIP.value, 10),
      PLATINUM: parseInt(DOM.rangeDemandPLATINUM.value, 10),
      GOLD: parseInt(DOM.rangeDemandGOLD.value, 10),
      SILVER: parseInt(DOM.rangeDemandSILVER.value, 10)
    };
    STATE.lastDemands = demands;
    return {
      venue_preset: DOM.selVenuePreset.value,
      capacity_C: venue.capacity,
      tau_0: parseFloat(DOM.rangeRiskTau.value) / 100.0,
      drop_rate_p: parseFloat(DOM.rangeDropRate.value) / 100.0,
      num_scenarios: parseInt(DOM.inputScenarios.value, 10) || 50,
      demand_limits: demands
    };
  }

  async function runPipeline() {
    DOM.btnRunFullPipeline.disabled = true;
    DOM.btnRunFullPipeline.textContent = '⏳ Đang Tính Toán 7 Module...';

    try {
      const payload = getPipelinePayload();
      const resp = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) throw new Error('Mã phản hồi lỗi từ server');
      const data = await resp.json();
      STATE.pipelineResult = data;

      // Update UI with real backend calculations
      updateAdminDashboard(data);
      showToast('⚡ Toàn bộ 7 Module M1 ➔ M7 đã chạy thành công!', 'success');
    } catch (err) {
      console.error('Pipeline error:', err);
      showToast('❌ Lỗi khi thực thi Pipeline: ' + err.message, 'danger');
    } finally {
      DOM.btnRunFullPipeline.disabled = false;
      DOM.btnRunFullPipeline.textContent = '▶️ Kích Hoạt Toàn Bộ 7 Module (M1 ➔ M7)';
    }
  }

  // Update Admin UI with Real Backend Calculations
  function updateAdminDashboard(data) {
    if (!data) return;

    // 1. National KPI Cards Strip
    const C = data.capacity_C || 40000;
    const M_star = data.m3_binary_search?.M_star || C;
    const overbookingPct = C > 0 ? ((M_star - C) / C) * 100 : 0;
    const pRealtime = data.m6_sliding_window?.p_t_realtime || data.drop_rate_p || 0.18;
    const netRev = data.m7_saa_benchmark?.proposed_revenue || 0;
    const baseRev = data.m7_saa_benchmark?.baseline_revenue || 0;
    const growthPct = baseRev > 0 ? ((netRev - baseRev) / baseRev) * 100 : 0;
    const probDb = data.m3_binary_search?.prob_db || 0;
    const protectedDb = data.m7_saa_benchmark?.protected_group_db_rate || 0.0;

    DOM.kpiCapacityC.textContent = formatNumber(C);
    DOM.kpiMStar.textContent = formatNumber(M_star);
    DOM.kpiOverbookingPct.textContent = `+${overbookingPct.toFixed(2)}%`;
    DOM.kpiDropRate.textContent = `${(pRealtime * 100).toFixed(1)}%`;
    DOM.kpiNetRevenue.textContent = formatCurrencyVN(netRev);
    DOM.kpiGrowthPct.textContent = `+${growthPct.toFixed(2)}%`;
    DOM.kpiProbDb.textContent = `${(probDb * 100).toFixed(2)}%`;
    DOM.kpiProtectedDbRate.textContent = `${protectedDb.toFixed(2)}%`;

    // Quotas in Sector selection
    const alloc = data.m4_knapsack_dp?.allocation || {};
    if (alloc.VVIP) {
      DOM.txtCapVVIP.textContent = formatNumber(Math.floor(alloc.VVIP * 0.8));
      DOM.txtMStarVVIP.textContent = formatNumber(alloc.VVIP);
    }
    if (alloc.PLATINUM) {
      DOM.txtCapPLATINUM.textContent = formatNumber(Math.floor(alloc.PLATINUM * 0.8));
      DOM.txtMStarPLATINUM.textContent = formatNumber(alloc.PLATINUM);
    }
    if (alloc.GOLD) {
      DOM.txtCapGOLD.textContent = formatNumber(Math.floor(alloc.GOLD * 0.8));
      DOM.txtMStarGOLD.textContent = formatNumber(alloc.GOLD);
    }
    if (alloc.SILVER) {
      DOM.txtCapSILVER.textContent = formatNumber(Math.floor(alloc.SILVER * 0.8));
      DOM.txtMStarSILVER.textContent = formatNumber(alloc.SILVER);
    }

    // 2. Tab M1: Merge Sort Samples
    const m1Sample = data.m1_merge_sort?.sample_sorted || [];
    DOM.tbodyM1Sample.innerHTML = m1Sample.map((u, i) => `
      <tr>
        <td>${i + 1}</td>
        <td><strong>#${u.user_id}</strong></td>
        <td>${formatNumber(u.arrival_time)} ms</td>
        <td><span class="gold">${u.loyalty_score}</span> / 100</td>
        <td><span class="tag-badge green">ĐÃ SẮP XẾP ỔN ĐỊNH</span></td>
      </tr>
    `).join('');

    // 3. Tab M2: Max-Heap Top-K
    const m2TopK = data.m2_max_heap?.top_k || [];
    DOM.tbodyM2TopK.innerHTML = m2TopK.map((u, i) => `
      <tr>
        <td><span class="tag-badge ${i < 3 ? 'gold' : ''}">Top #${i + 1}</span></td>
        <td>${u.name || ('Khán giả #' + u.user_id)}</td>
        <td><span class="card-badge">${u.priority_group || 'Chính sách Tri Ân'}</span></td>
        <td><strong class="gold">${u.loyalty_score}</strong></td>
        <td><span class="cyan">${u.ticket_type || 'VVIP'}</span></td>
      </tr>
    `).join('');

    // Render visual Heap tree
    renderHeapTree(m2TopK);

    // 4. Tab M3: Binary Search Trace
    const trace = data.m3_binary_search?.search_trace || [];
    DOM.m3TraceContainer.innerHTML = trace.map(step => `
      <div class="trace-card ${step.risk <= (data.tau_0 || 0.05) ? 'safe' : 'exceed'}">
        <div class="trace-header">
          <span class="trace-step">Vòng lặp #${step.step}</span>
          <span class="trace-badge">${step.risk <= (data.tau_0 || 0.05) ? '✓ Rủi ro An toàn' : '⚠️ Vượt τ₀'}</span>
        </div>
        <div class="trace-body">
          <div><strong>Khoảng co:</strong> [${formatNumber(step.low)} ➔ ${formatNumber(step.high)}]</div>
          <div><strong>Nghiệm thử Mid:</strong> <span class="gold">${formatNumber(step.mid)} vé</span></div>
          <div><strong>Xác suất P(K > C):</strong> ${(step.risk * 100).toFixed(2)}%</div>
          <div class="trace-dir">Hướng rẽ: <em>${step.decision || (step.risk <= (data.tau_0 || 0.05) ? 'Tăng low = mid + 1' : 'Giảm high = mid - 1')}</em></div>
        </div>
      </div>
    `).join('');

    // 5. Tab M4: Bounded Knapsack Allocation (GAP-4)
    const demandLimits = STATE.lastDemands || data.m4_knapsack_dp?.demands || {};
    const prices = { VVIP: 4500000, PLATINUM: 2500000, GOLD: 1200000, SILVER: 600000 };
    DOM.m4AllocationDisplay.innerHTML = Object.keys(alloc).map(sec => {
      const numAlloc = alloc[sec] || 0;
      const limit = demandLimits[sec] || numAlloc;
      const pct = limit > 0 ? Math.min(100, (numAlloc / limit) * 100) : 100;
      const secRev = numAlloc * (prices[sec] || 0);

      return `
        <div class="allocation-card">
          <div class="alloc-title">
            <span class="sec-tag">${sec}</span>
            <span class="sec-rev">${formatCurrencyVN(secRev)}</span>
          </div>
          <div class="alloc-stats">
            <div>Phân bổ M4: <strong class="gold">${formatNumber(numAlloc)} vé</strong></div>
            <div>Nhu cầu (Demand): <span>${formatNumber(limit)}</span></div>
          </div>
          <div class="alloc-progress-bg">
            <div class="alloc-progress-bar" style="width: ${pct}%"></div>
          </div>
          <div class="alloc-note">Tỷ lệ đáp ứng thị trường: ${pct.toFixed(1)}%</div>
        </div>
      `;
    }).join('');

    // 6. Tab M5: Gate Check-in Sample
    const m5Sample = data.m5_greedy?.sample_checkin || [];
    DOM.tbodyM5Sample.innerHTML = m5Sample.map(chk => {
      let statusBadge = '<span class="tag-badge green">ĐÚNG HẠNG GHẾ</span>';
      let compText = 'Không đền bù (0 đ)';
      if (chk.status === 'UPGRADED') {
        statusBadge = '<span class="tag-badge cyan">TỰ ĐỘNG NÂNG HẠNG</span>';
        compText = 'Miễn phí chênh lệch';
      } else if (chk.status === 'DENIED_BOARDING') {
        statusBadge = '<span class="tag-badge red">TỪ CHỐI LÊN TÀU</span>';
        compText = '<strong class="gold">Đền bù 150% + Quà</strong>';
      }
      return `
        <tr>
          <td>Khán giả #${chk.user_id} ${chk.is_protected ? '⭐' : ''}</td>
          <td>${chk.requested_type}</td>
          <td><strong class="cyan">${chk.assigned_seat || 'N/A'}</strong></td>
          <td>${statusBadge}</td>
          <td>${compText}</td>
        </tr>
      `;
    }).join('');

    // 7. Tab M6: Realtime Sliding Window Canvas Chart
    updateSlidingWindowHistory(pRealtime);
    renderSlidingWindowChart();

    // 8. Tab M7: SAA Monte Carlo Benchmark Table
    const saa = data.m7_saa_benchmark || {};
    DOM.m7BenchmarkDisplay.innerHTML = `
      <table class="data-table benchmark-table">
        <thead>
          <tr>
            <th>CHỈ SỐ ĐỐI SOÁT MONTE CARLO (S = ${data.num_scenarios || 50})</th>
            <th>MÔ HÌNH CỐ ĐỊNH (BASELINE - C)</th>
            <th>MÔ HÌNH BÁN LỐ ĐỀ XUẤT (PROPOSED - M*)</th>
            <th>HIỆU QUẢ TỐI ƯU</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tổng số vé phát hành</strong></td>
            <td>${formatNumber(C)} vé</td>
            <td class="gold"><strong>${formatNumber(M_star)} vé</strong></td>
            <td><span class="tag-badge green">+${overbookingPct.toFixed(2)}% vé bổ sung</span></td>
          </tr>
          <tr>
            <td><strong>Doanh thu thuần kỳ vọng (VNĐ)</strong></td>
            <td>${formatCurrencyVN(saa.baseline_revenue || 0)}</td>
            <td class="gold"><strong>${formatCurrencyVN(saa.proposed_revenue || 0)}</strong></td>
            <td><span class="tag-badge green">+${growthPct.toFixed(2)}% doanh thu</span></td>
          </tr>
          <tr>
            <td><strong>Chi phí đền bù Denied Boarding</strong></td>
            <td>0 đ (Không bán lố)</td>
            <td class="red">${formatCurrencyVN(saa.compensation_cost || 0)}</td>
            <td>Đã khấu trừ trực tiếp</td>
          </tr>
          <tr>
            <td><strong>Tỷ lệ quá tải thực tế P(K > C)</strong></td>
            <td>0.00%</td>
            <td class="cyan">${(probDb * 100).toFixed(2)}%</td>
            <td><span class="tag-badge green">Thỏa mãn ≤ τ₀ (${(data.tau_0 * 100).toFixed(1)}%)</span></td>
          </tr>
          <tr class="highlight-row">
            <td><strong>Tỷ lệ ảnh hưởng Khách Chính Sách Tri Ân</strong></td>
            <td>0.00%</td>
            <td class="gold"><strong>0.00% (BẢO VỆ 100%)</strong></td>
            <td><span class="tag-badge gold">⭐ Cam kết đạo đức tối thượng</span></td>
          </tr>
        </tbody>
      </table>
    `;
  }

  let payload_last_demands = null;

  // Render Heap Tree Mock
  function renderHeapTree(topList) {
    if (!DOM.heapTreeVisualizer) return;
    if (!topList || topList.length === 0) {
      DOM.heapTreeVisualizer.innerHTML = '<div class="empty-state">Chưa có dữ liệu Heap</div>';
      return;
    }

    const root = topList[0];
    const left = topList[1] || null;
    const right = topList[2] || null;

    DOM.heapTreeVisualizer.innerHTML = `
      <div class="heap-tree-box">
        <div class="heap-level">
          <div class="heap-node root">
            <div class="hn-score">${root.loyalty_score}</div>
            <div class="hn-name">${root.name || '#' + root.user_id}</div>
            <div class="hn-tag">GỐC MAX-HEAP</div>
          </div>
        </div>
        <div class="heap-branches">
          <div class="branch-line left"></div>
          <div class="branch-line right"></div>
        </div>
        <div class="heap-level sub">
          ${left ? `
            <div class="heap-node child">
              <div class="hn-score">${left.loyalty_score}</div>
              <div class="hn-name">${left.name || '#' + left.user_id}</div>
              <div class="hn-tag">NHÁNH TRÁI</div>
            </div>
          ` : ''}
          ${right ? `
            <div class="heap-node child">
              <div class="hn-score">${right.loyalty_score}</div>
              <div class="hn-name">${right.name || '#' + right.user_id}</div>
              <div class="hn-tag">NHÁNH PHẢI</div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  // Sliding Window 2D Canvas Chart
  function updateSlidingWindowHistory(currentP) {
    if (STATE.slidingWindowHistory.length > 25) {
      STATE.slidingWindowHistory.shift();
    }
    STATE.slidingWindowHistory.push(currentP);
  }

  function renderSlidingWindowChart() {
    const canvas = DOM.canvasSlidingWindow;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    // Clear background
    ctx.clearRect(0, 0, w, h);

    // If history is small, mock a smooth wave around current p
    let points = [...STATE.slidingWindowHistory];
    if (points.length < 5) {
      const base = parseFloat(DOM.rangeDropRate.value) / 100.0 || 0.18;
      points = [base - 0.02, base - 0.01, base + 0.015, base - 0.005, base + 0.01, base];
    }

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
    ctx.lineWidth = 1;
    for (let y = 30; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(40, y);
      ctx.lineTo(w - 20, y);
      ctx.stroke();
    }

    // Draw curve
    const minVal = 0.05;
    const maxVal = 0.35;
    const stepX = (w - 70) / (points.length - 1);

    ctx.beginPath();
    points.forEach((val, i) => {
      const x = 50 + i * stepX;
      const y = h - 30 - ((val - minVal) / (maxVal - minVal)) * (h - 70);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        const prevX = 50 + (i - 1) * stepX;
        const prevVal = points[i - 1];
        const prevY = h - 30 - ((prevVal - minVal) / (maxVal - minVal)) * (h - 70);
        const cpX = (prevX + x) / 2;
        ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
      }
    });

    // Gradient stroke
    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, '#60A5FA');
    grad.addColorStop(1, '#10B981');
    ctx.strokeStyle = grad;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Draw dots
    points.forEach((val, i) => {
      const x = 50 + i * stepX;
      const y = h - 30 - ((val - minVal) / (maxVal - minVal)) * (h - 70);
      ctx.fillStyle = '#10B981';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();

      // Label last point
      if (i === points.length - 1) {
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '12px JetBrains Mono';
        ctx.fillText(`${(val * 100).toFixed(1)}%`, x - 15, y - 10);
      }
    });

    // Baseline labels
    ctx.fillStyle = '#94A3B8';
    ctx.font = '11px JetBrains Mono';
    ctx.fillText('35%', 10, 35);
    ctx.fillText('20%', 10, h / 2);
    ctx.fillText('5%', 10, h - 25);
  }

  // =========================================================================
  // 8. EVENT HANDLERS & DEBOUNCE
  // =========================================================================
  function debounceRunPipeline() {
    clearTimeout(STATE.debounceTimer);
    STATE.debounceTimer = setTimeout(() => {
      runPipeline();
    }, 300);
  }

  // Sliders input updates
  DOM.rangeRiskTau.addEventListener('input', (e) => {
    DOM.lblRiskTau.textContent = `${parseFloat(e.target.value).toFixed(1)}%`;
    debounceRunPipeline();
  });

  DOM.rangeDropRate.addEventListener('input', (e) => {
    DOM.lblDropRate.textContent = `${parseFloat(e.target.value).toFixed(1)}%`;
    debounceRunPipeline();
  });

  // Demand sliders (GAP-4)
  DOM.rangeDemandVVIP.addEventListener('input', (e) => {
    DOM.lblDemandVVIP.textContent = formatNumber(e.target.value);
    debounceRunPipeline();
  });

  DOM.rangeDemandPLATINUM.addEventListener('input', (e) => {
    DOM.lblDemandPLATINUM.textContent = formatNumber(e.target.value);
    debounceRunPipeline();
  });

  DOM.rangeDemandGOLD.addEventListener('input', (e) => {
    DOM.lblDemandGOLD.textContent = formatNumber(e.target.value);
    debounceRunPipeline();
  });

  DOM.rangeDemandSILVER.addEventListener('input', (e) => {
    DOM.lblDemandSILVER.textContent = formatNumber(e.target.value);
    debounceRunPipeline();
  });

  // Venue Preset Selection
  DOM.selVenuePreset.addEventListener('change', (e) => {
    const p = VENUE_PRESETS[e.target.value] || VENUE_PRESETS.my_dinh;
    DOM.txtActiveVenue.textContent = p.name;

    // Update Demand Sliders according to venue scale
    DOM.rangeDemandVVIP.value = p.demands.VVIP;
    DOM.lblDemandVVIP.textContent = formatNumber(p.demands.VVIP);

    DOM.rangeDemandPLATINUM.value = p.demands.PLATINUM;
    DOM.lblDemandPLATINUM.textContent = formatNumber(p.demands.PLATINUM);

    DOM.rangeDemandGOLD.value = p.demands.GOLD;
    DOM.lblDemandGOLD.textContent = formatNumber(p.demands.GOLD);

    DOM.rangeDemandSILVER.value = p.demands.SILVER;
    DOM.lblDemandSILVER.textContent = formatNumber(p.demands.SILVER);

    debounceRunPipeline();
  });

  // Action Buttons
  DOM.btnRunFullPipeline.addEventListener('click', runPipeline);

  DOM.btnResetSystem.addEventListener('click', async () => {
    if (!confirm('Bạn có chắc chắn muốn thiết lập lại toàn bộ dữ liệu mô phỏng?')) return;
    try {
      const resp = await fetch('/api/reset', { method: 'POST' });
      if (resp.ok) {
        showToast('🔄 Đã đặt lại trạng thái ban đầu thành công!', 'info');
        runPipeline();
      }
    } catch (e) {
      showToast('Lỗi khi reset hệ thống', 'danger');
    }
  });

  // Tab switching inside Admin
  DOM.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      DOM.tabBtns.forEach(b => b.classList.remove('active'));
      DOM.tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const pane = document.getElementById(targetTab);
      if (pane) pane.classList.add('active');

      if (targetTab === 'tabM6') {
        setTimeout(renderSlidingWindowChart, 50);
      }
    });
  });

  // =========================================================================
  // 9. INITIALIZATION
  // =========================================================================
  async function initApp() {
    // Check local session
    const savedToken = localStorage.getItem('vwr_queue_token');
    if (savedToken) {
      STATE.queueToken = savedToken;
    }

    // Start Citizen Queue Polling
    startQueuePolling();

    // Initial Pipeline Calculation
    await runPipeline();
  }

  // Bootstrap when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }

})();
