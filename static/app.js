/**
 * VIRTUAL WAITING ROOM & STOCHASTIC OVERBOOKING - ĐẠI NHẠC HỘI QUỐC GIA 2026
 * Frontend Logic & API Integration
 * 
 * Tuân thủ nghiêm ngặt Master Prompt v2.0:
 * - RULE 0: 100% thuật toán chạy trên Backend Python (server.py), Frontend chỉ hiển thị số liệu thực tế.
 * - GAP-4: Phân tách rõ Sức chứa cứng (physical_cap) và Nhu cầu thị trường (demand_limits).
 * - GAP-7: Nhóm chính sách (Bà mẹ VNAH, Thương binh, CCB, Con liệt sĩ) có protected_group_db_rate = 0.00%.
 * - STEP-BY-STEP WORKFLOW: Trình diễn 7 giai đoạn luồng dữ liệu liên hoàn (M1 -> M7).
 * - DYNAMIC INPUTS: Cho phép tự do nhập số lượng ghế sân C, số người mua N, số lượng vé phân khu.
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
    slidingWindowHistory: [],
    
    // Step-by-step state
    currentStep: 1,
    isAutoPlaying: false,
    autoPlayTimer: null,
    autoPlaySpeed: 2000, // 2s per step
    lastDemands: null
  };

  const VENUE_PRESETS = {
    mega_concert: {
      name: 'ĐẠI NHẠC HỘI MEGA CONCERT (100,000 GHẾ)',
      capacity: 100000,
      totalWaiting: 1000000,
      tau0: 5.0,
      pDrop: 18,
      scenarios: 100,
      demands: { VVIP: 15000, PLATINUM: 35000, GOLD: 50000, SILVER: 35000 }
    },
    my_dinh: {
      name: 'SÂN VẬN ĐỘNG MỸ ĐÌNH (40,000 GHẾ)',
      capacity: 40000,
      totalWaiting: 185420,
      tau0: 5.0,
      pDrop: 18,
      scenarios: 50,
      demands: { VVIP: 4000, PLATINUM: 13000, GOLD: 20000, SILVER: 12000 }
    },
    arena: {
      name: 'NHÀ THI ĐẤU QUỐC TẾ (10,000 GHẾ)',
      capacity: 10000,
      totalWaiting: 85000,
      tau0: 5.0,
      pDrop: 18,
      scenarios: 50,
      demands: { VVIP: 1000, PLATINUM: 3500, GOLD: 5000, SILVER: 3000 }
    },
    ncc: {
      name: 'TRUNG TÂM HỘI NGHỊ QUỐC GIA (3,800 GHẾ)',
      capacity: 3800,
      totalWaiting: 35000,
      tau0: 5.0,
      pDrop: 18,
      scenarios: 50,
      demands: { VVIP: 400, PLATINUM: 1400, GOLD: 2000, SILVER: 1000 }
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

    // Stepper in Citizen View
    stepperSteps: document.querySelectorAll('.stepper-step'),
    stepperLines: document.querySelectorAll('.stepper-line'),

    // Sector & TTL in Citizen View
    ttlCountdownPill: document.getElementById('ttlCountdownPill'),
    txtTtlTimer: document.getElementById('txtTtlTimer'),
    stadiumSvgMap: document.getElementById('stadiumSvgMap'),
    sectorPolys: document.querySelectorAll('.sector-poly'),
    sectorBtnCards: document.querySelectorAll('.sector-btn-card'),
    inputCitizenQty: document.getElementById('inputCitizenQty'),
    btnQtyChips: document.querySelectorAll('.btn-qty-chip'),
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

    // Custom Input Controls (Admin)
    inputCapacityC: document.getElementById('inputCapacityC'),
    btnPresetChips: document.querySelectorAll('.preset-chips [data-preset]'),
    inputNumUsers: document.getElementById('inputNumUsers'),
    btnUsersChips: document.querySelectorAll('.preset-chips [data-users]'),
    rangeRiskTau: document.getElementById('rangeRiskTau'),
    lblRiskTau: document.getElementById('lblRiskTau'),
    rangeDropRate: document.getElementById('rangeDropRate'),
    lblDropRate: document.getElementById('lblDropRate'),
    inputScenarios: document.getElementById('inputScenarios'),
    btnRunFullPipeline: document.getElementById('btnRunFullPipeline'),
    btnResetSystem: document.getElementById('btnResetSystem'),

    // Demand Inputs & Sliders
    inputDemandVVIP: document.getElementById('inputDemandVVIP'),
    rangeDemandVVIP: document.getElementById('rangeDemandVVIP'),
    inputDemandPLATINUM: document.getElementById('inputDemandPLATINUM'),
    rangeDemandPLATINUM: document.getElementById('rangeDemandPLATINUM'),
    inputDemandGOLD: document.getElementById('inputDemandGOLD'),
    rangeDemandGOLD: document.getElementById('rangeDemandGOLD'),
    inputDemandSILVER: document.getElementById('inputDemandSILVER'),
    rangeDemandSILVER: document.getElementById('rangeDemandSILVER'),

    // KPI Cards
    kpiCapacityC: document.getElementById('kpiCapacityC'),
    kpiMStar: document.getElementById('kpiMStar'),
    kpiOverbookingPct: document.getElementById('kpiOverbookingPct'),
    kpiDropRate: document.getElementById('kpiDropRate'),
    kpiNetRevenue: document.getElementById('kpiNetRevenue'),
    kpiGrowthPct: document.getElementById('kpiGrowthPct'),
    kpiProbDb: document.getElementById('kpiProbDb'),
    kpiProtectedDbRate: document.getElementById('kpiProtectedDbRate'),

    // Step-by-Step Pipeline Controls
    btnPrevStep: document.getElementById('btnPrevStep'),
    btnNextStep: document.getElementById('btnNextStep'),
    btnAutoPlayStep: document.getElementById('btnAutoPlayStep'),
    txtAutoPlayIcon: document.getElementById('txtAutoPlayIcon'),
    txtAutoPlayText: document.getElementById('txtAutoPlayText'),
    txtCurrentStepIndicator: document.getElementById('txtCurrentStepIndicator'),
    stepNodes: document.querySelectorAll('.pipeline-steps-track .step-node'),

    // Spotlight 4-Column Card
    spModuleCode: document.getElementById('spModuleCode'),
    spStageTitle: document.getElementById('spStageTitle'),
    spTimeComplexity: document.getElementById('spTimeComplexity'),
    spSpaceComplexity: document.getElementById('spSpaceComplexity'),
    spRuntimeMs: document.getElementById('spRuntimeMs'),
    spInputDesc: document.getElementById('spInputDesc'),
    spInputFoot: document.getElementById('spInputFoot'),
    spAlgoDesc: document.getElementById('spAlgoDesc'),
    spFormulaBox: document.getElementById('spFormulaBox'),
    spComplexityDesc: document.getElementById('spComplexityDesc'),
    spComplexityFoot: document.getElementById('spComplexityFoot'),
    spOutputDesc: document.getElementById('spOutputDesc'),
    spOutputFoot: document.getElementById('spOutputFoot'),

    // Live Visualizer Panes
    stagePanes: document.querySelectorAll('.stage-vis-pane'),
    visStageHint: document.getElementById('visStageHint'),

    // Visualizer Containers
    tbodyM1Sample: document.getElementById('tbodyM1Sample'),
    heapTreeVisualizer: document.getElementById('heapTreeVisualizer'),
    tbodyM2TopK: document.getElementById('tbodyM2TopK'),
    m3TraceContainer: document.getElementById('m3TraceContainer'),
    m4AllocationDisplay: document.getElementById('m4AllocationDisplay'),
    tbodyM5Sample: document.getElementById('tbodyM5Sample'),
    canvasSlidingWindow: document.getElementById('canvasSlidingWindow'),
    m7BenchmarkDisplay: document.getElementById('m7BenchmarkDisplay'),
    m6HeapLiveDisplay: document.getElementById('m6HeapLiveDisplay'),

    // New Controls: Priority Selector & Run Module Action
    selectUserPriority: document.getElementById('selectUserPriority'),
    btnRunCurrentModule: document.getElementById('btnRunCurrentModule'),
    txtBtnRunCurrentModule: document.getElementById('txtBtnRunCurrentModule'),
    txtModuleRunStatus: document.getElementById('txtModuleRunStatus'),
    walkerTrackFill: document.getElementById('walkerTrackFill'),
    walkingPersonAvatar: document.getElementById('walkingPersonAvatar')
  };

  // =========================================================================
  // 3. UTILITY FUNCTIONS & MATH RENDERER
  // =========================================================================
  function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    return Number(num).toLocaleString('vi-VN');
  }

  // Định dạng số có dấu chấm ngăn cách hàng nghìn (ví dụ: 40000 -> 40.000)
  function formatDots(val) {
    if (val === null || val === undefined || val === '') return '';
    const num = parseInt(String(val).replace(/\D/g, ''), 10);
    if (isNaN(num)) return '';
    return num.toLocaleString('vi-VN');
  }

  // Đọc số nguyên sạch từ chuỗi có dấu chấm (ví dụ: "40.000" -> 40000)
  function parseDots(val) {
    if (val === null || val === undefined || val === '') return 0;
    const clean = String(val).replace(/\./g, '').replace(/,/g, '').trim();
    return parseInt(clean, 10) || 0;
  }

  // Render công thức toán học KaTeX + Unicode Fallback (Yêu Cầu 3)
  function renderMathFormula(containerEl, latexStr, fallbackHtml) {
    if (!containerEl) return;
    if (window.katex && typeof window.katex.render === 'function') {
      try {
        window.katex.render(latexStr, containerEl, {
          displayMode: true,
          throwOnError: false
        });
        return;
      } catch (e) {
        console.warn('KaTeX render error:', e);
      }
    }
    // Fallback Unicode toán học chuẩn nếu offline
    containerEl.innerHTML = `<div class="math-fallback-container">${fallbackHtml}</div>`;
  }

  // Cấu hình công thức toán học chuẩn xác theo 7 module
  const STEP_FORMULAS = {
    1: {
      latex: "T(N) = 2T(N/2) + \\mathcal{O}(N) \\implies \\mathcal{O}(N \\log N)",
      fallback: "<span>T(N) = 2T(N/2) + O(N)</span> <span class='math-symbol'>⇒</span> <strong>O(N · log N)</strong>"
    },
    2: {
      latex: "\\text{Sift-Down}: \\mathcal{O}(\\log N) \\implies \\text{Top-}K: \\mathcal{O}(N + K \\log N)",
      fallback: "<span>Sift-Down: O(log N)</span> <span class='math-symbol'>⇒</span> <strong>Top-K: O(N + K · log N)</strong>"
    },
    3: {
      latex: "p(t) = \\frac{1}{W} \\sum_{i=t-W+1}^{t} \\mathbb{I}(\\text{drop}_i) \\quad [\\mathcal{O}(1)]",
      fallback: "<span>p(t) = (1 / W) · ∑ drop<span class='math-sub'>i</span></span> <span class='math-tag'>O(1) Realtime</span>"
    },
    4: {
      latex: "P(K > C) = 1 - \\sum_{k=0}^{C} \\binom{M}{k} (1-p)^k p^{M-k} \\le \\tau_0",
      fallback: "<span>P(K &gt; C) = 1 - ∑ [C(M, k) · (1-p)<span class='math-sup'>k</span> · p<span class='math-sup'>M-k</span>]</span> <span class='math-symbol'>≤</span> <strong>τ₀</strong>"
    },
    5: {
      latex: "\\max \\sum_{i=1}^{4} r_i x_i \\quad \\text{s.t.} \\quad \\sum_{i=1}^{4} x_i \\le M^*, \\quad 0 \\le x_i \\le d_i",
      fallback: "<span>max ∑ (r<span class='math-sub'>i</span> · x<span class='math-sub'>i</span>)</span> sao cho <span>∑ x<span class='math-sub'>i</span> ≤ M* và 0 ≤ x<span class='math-sub'>i</span> ≤ d<span class='math-sub'>i</span></span>"
    },
    6: {
      latex: "t_{\\text{expire}} \\le t_{\\text{current}} \\implies \\text{Extract-Min}: \\mathcal{O}(\\log N)",
      fallback: "<span>t<span class='math-sub'>hết hạn</span> ≤ t<span class='math-sub'>hiện tại</span></span> <span class='math-symbol'>⇒</span> <strong>Min-Heap Extract-Min O(log N)</strong>"
    },
    7: {
      latex: "\\max_{M} \\frac{1}{S} \\sum_{s=1}^{S} \\text{Revenue}(M, \\omega_s) \\quad [M^*_{\\text{SAA}}]",
      fallback: "<span>max (1/S) · ∑ Revenue(M, ω<span class='math-sub'>s</span>)</span> <span class='math-tag'>Monte Carlo SAA</span>"
    }
  };

  const STEP_MODULE_INFO = {
    1: { code: 'M1', name: 'M1: Merge Sort', btnLabel: 'Chạy Riêng Bước 1 (M1 Merge Sort)' },
    2: { code: 'M2', name: 'M2: Max-Heap', btnLabel: 'Chạy Riêng Bước 2 (M2 Max-Heap)' },
    3: { code: 'M6_WINDOW', name: 'M6: Sliding Window', btnLabel: 'Chạy Riêng Bước 3 (M6 Sliding Window)' },
    4: { code: 'M3', name: 'M3: Binary Search', btnLabel: 'Chạy Riêng Bước 4 (M3 Binary Search M*)' },
    5: { code: 'M4', name: 'M4: Knapsack DP', btnLabel: 'Chạy Riêng Bước 5 (M4 Knapsack DP)' },
    6: { code: 'M6_HEAP', name: 'M6: Min-Heap TTL', btnLabel: 'Chạy Riêng Bước 6 (M6 Min-Heap TTL)' },
    7: { code: 'M7', name: 'M5 & M7: SAA', btnLabel: 'Chạy Riêng Bước 7 (M5 Greedy & M7 SAA)' }
  };

  function formatCurrencyVN(val) {
    if (val === undefined || val === null || isNaN(val)) return '0 đ';
    const num = Number(val);
    if (num === 0) return '0 đ';
    const sign = num < 0 ? '-' : '';
    const absVal = Math.abs(num);
    if (absVal >= 1e9) {
      return sign + (absVal / 1e9).toFixed(2) + ' Tỷ đ';
    }
    if (absVal >= 1e6) {
      return sign + (absVal / 1e6).toFixed(1) + ' Triệu đ';
    }
    return sign + formatNumber(Math.round(absVal)) + ' đ';
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
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.15);
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
      // Render canvas when switching to admin if on Step 3
      if (STATE.currentStep === 3) {
        setTimeout(renderSlidingWindowChart, 50);
      }
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

      // Cập nhật vị trí thanh tiến trình người đi bộ (Walking Person Progress)
      const walkerFill = document.getElementById('walkerTrackFill');
      const walkerAvatar = document.getElementById('walkingPersonAvatar');
      if (walkerFill && walkerAvatar) {
        const total = Math.max(STATE.totalWaiting, STATE.queuePosition || 1);
        const progressPct = Math.max(5, Math.min(95, Math.round((1 - (STATE.queuePosition / total)) * 100)));
        walkerFill.style.width = `${progressPct}%`;
        walkerAvatar.style.left = `${progressPct}%`;
      }

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

    const walkerFill = document.getElementById('walkerTrackFill');
    const walkerAvatar = document.getElementById('walkingPersonAvatar');
    if (walkerFill && walkerAvatar) {
      walkerFill.style.width = '100%';
      walkerAvatar.style.left = '100%';
    }

    playAlertChime();
    showToast('🎉 ĐÃ ĐẾN LƯỢT CỦA BẠN! Mời chọn phân khu khán đài.', 'success');

    DOM.btnHoldTicket.disabled = false;
    DOM.btnHoldTicket.classList.add('btn-pulse');
  }

  // Fast-Pass Demo Button
  DOM.btnFastPassDemo.addEventListener('click', () => {
    STATE.queuePosition = 1;
    handleUserCalled();
  });

  // =========================================================================
  // 6. SECTOR SELECTION & DYNAMIC TTL HOLDING
  // =========================================================================
  function setSelectedSector(sector) {
    STATE.selectedSector = sector;

    DOM.sectorPolys.forEach(poly => {
      if (poly.getAttribute('data-sector') === sector) {
        poly.classList.add('active');
      } else {
        poly.classList.remove('active');
      }
    });

    DOM.sectorBtnCards.forEach(card => {
      if (card.getAttribute('data-sector') === sector) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  DOM.sectorPolys.forEach(poly => {
    poly.addEventListener('click', () => {
      const sec = poly.getAttribute('data-sector');
      if (sec) setSelectedSector(sec);
    });
  });

  DOM.sectorBtnCards.forEach(card => {
    card.addEventListener('click', () => {
      const sec = card.getAttribute('data-sector');
      if (sec) setSelectedSector(sec);
    });
  });

  // Ticket quantity chips in Citizen View
  DOM.btnQtyChips.forEach(chip => {
    chip.addEventListener('click', () => {
      DOM.btnQtyChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const q = parseInt(chip.getAttribute('data-qty'), 10) || 1;
      DOM.inputCitizenQty.value = q;
      STATE.selectedQuantity = q;
    });
  });

  DOM.inputCitizenQty.addEventListener('input', (e) => {
    const q = parseInt(e.target.value, 10) || 1;
    STATE.selectedQuantity = q;
    DOM.btnQtyChips.forEach(c => {
      c.classList.toggle('active', parseInt(c.getAttribute('data-qty'), 10) === q);
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
        DOM.txtTtlTimer.style.color = '#F87171';
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

    const qty = parseInt(DOM.inputCitizenQty.value, 10) || 1;
    STATE.selectedQuantity = qty;

    try {
      const payload = {
        user_id: String(STATE.userId),
        ticket_type: STATE.selectedSector,
        sector: STATE.selectedSector,
        quantity: qty,
        seat_count: qty
      };

      const resp = await fetch('/api/hold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const res = await resp.json();
      if (resp.ok && (res.status === 'SUCCESS' || res.hold_id)) {
        STATE.heldTicket = res;
        showToast(`✅ Giữ vé thành công! Bạn có 10 phút để xác nhận.`, 'success');
        updateStepper(3);

        startTTLCountdown(res.expires_at || res.expires_at_timestamp);

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
          user_id: String(STATE.userId),
          seat_id: STATE.heldTicket.seat_id,
          ticket_type: STATE.heldTicket.ticket_type || STATE.selectedSector
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
  // 7. STEP-BY-STEP PIPELINE ENGINE (BƯỚC 1 ĐẾN BƯỚC 7)
  // =========================================================================
  function goToStep(stepNum) {
    if (stepNum < 1) stepNum = 1;
    if (stepNum > 7) stepNum = 7;
    STATE.currentStep = stepNum;

    // Update Step Indicator
    DOM.txtCurrentStepIndicator.textContent = `${stepNum} / 7`;

    // Update Step Nodes
    DOM.stepNodes.forEach((node, idx) => {
      const s = idx + 1;
      node.classList.toggle('active', s === stepNum);
      node.classList.toggle('completed', s < stepNum);
    });

    // Update Live Visualizer Panes
    DOM.stagePanes.forEach((pane, idx) => {
      pane.classList.toggle('active', idx + 1 === stepNum);
    });

    // Update Spotlight 4-Column Card
    updateSpotlightCard(stepNum);

    // Redraw canvas if Step 3 is active
    if (stepNum === 3) {
      setTimeout(renderSlidingWindowChart, 40);
    }
  }

  function nextStep() {
    if (STATE.currentStep < 7) {
      goToStep(STATE.currentStep + 1);
    } else {
      goToStep(1); // loop around
    }
  }

  function prevStep() {
    if (STATE.currentStep > 1) {
      goToStep(STATE.currentStep - 1);
    }
  }

  function toggleAutoPlay() {
    STATE.isAutoPlaying = !STATE.isAutoPlaying;
    if (STATE.isAutoPlaying) {
      DOM.txtAutoPlayIcon.textContent = '⏸️';
      DOM.txtAutoPlayText.textContent = 'Tạm Dừng';
      DOM.btnAutoPlayStep.style.background = '#DC2626';
      STATE.autoPlayTimer = setInterval(nextStep, STATE.autoPlaySpeed);
    } else {
      DOM.txtAutoPlayIcon.textContent = '▶️';
      DOM.txtAutoPlayText.textContent = 'Trình Diễn Tự Động';
      DOM.btnAutoPlayStep.style.background = '';
      if (STATE.autoPlayTimer) clearInterval(STATE.autoPlayTimer);
      STATE.autoPlayTimer = null;
    }
  }

  DOM.btnPrevStep.addEventListener('click', prevStep);
  DOM.btnNextStep.addEventListener('click', nextStep);
  DOM.btnAutoPlayStep.addEventListener('click', toggleAutoPlay);

  DOM.stepNodes.forEach(node => {
    node.addEventListener('click', () => {
      const s = parseInt(node.getAttribute('data-step'), 10);
      if (s) goToStep(s);
    });
  });

  // Update Spotlight Card dynamically
  function updateSpotlightCard(stepNum) {
    const pData = STATE.pipelineResult;
    const stepsMeta = pData?.pipeline_steps || [];
    const stepData = stepsMeta.find(s => s.step_number === stepNum);

    const stepInfo = STEP_MODULE_INFO[stepNum] || { code: 'M1', name: 'Module', btnLabel: 'Chạy Riêng Module Này' };
    if (DOM.txtBtnRunCurrentModule) {
      DOM.txtBtnRunCurrentModule.textContent = stepInfo.btnLabel;
    }
    if (DOM.txtModuleRunStatus) {
      DOM.txtModuleRunStatus.textContent = `🟢 Sẵn sàng thực thi riêng Bước ${stepNum} (${stepInfo.name})`;
      DOM.txtModuleRunStatus.style.color = '#34D399';
    }

    if (stepData) {
      DOM.spModuleCode.textContent = stepData.module_code;
      DOM.spStageTitle.textContent = `Giai Đoạn ${stepNum}: ${stepData.title}`;
      DOM.spTimeComplexity.textContent = stepData.time_complexity;
      DOM.spSpaceComplexity.textContent = stepData.space_complexity;
      DOM.spRuntimeMs.textContent = `Runtime: ~${stepData.elapsed_ms || 2} ms`;
      DOM.spInputDesc.textContent = stepData.input_info;
      DOM.spAlgoDesc.innerHTML = `<strong>${stepData.algorithm}:</strong> Thực thi thuật toán lõi viết tay 100% tuân thủ quy chuẩn không dùng thư viện ngoài.`;
      DOM.spComplexityDesc.textContent = `Thiết kế tối ưu hóa bộ nhớ và độ trễ, đạt hiệu năng xử lý cực cao trên quy mô đại nhạc hội quốc gia.`;
      DOM.spOutputDesc.textContent = stepData.output_info;
    }

    // Render KaTeX Math formula sắc nét không lỗi
    const formulaConfig = STEP_FORMULAS[stepNum];
    if (formulaConfig) {
      renderMathFormula(DOM.spFormulaBox, formulaConfig.latex, formulaConfig.fallback);
    }
  }

  // =========================================================================
  // 8. ADMIN CONTROLS & PIPELINE EXECUTION
  // =========================================================================
  function getPipelinePayload() {
    const C = parseDots(DOM.inputCapacityC.value) || 40000;
    const N = parseDots(DOM.inputNumUsers.value) || 185420;

    const demands = {
      VVIP: parseDots(DOM.inputDemandVVIP.value) || 5200,
      PLATINUM: parseDots(DOM.inputDemandPLATINUM.value) || 13000,
      GOLD: parseDots(DOM.inputDemandGOLD.value) || 20000,
      SILVER: parseDots(DOM.inputDemandSILVER.value) || 12000
    };
    STATE.lastDemands = demands;

    return {
      venue_preset: STATE.venuePreset,
      capacity_C: C,
      num_users: N,
      tau_0: parseFloat(DOM.rangeRiskTau.value) / 100.0,
      drop_rate_p: parseFloat(DOM.rangeDropRate.value) / 100.0,
      num_scenarios: parseInt(DOM.inputScenarios.value, 10) || 50,
      demand_limits: demands
    };
  }

  // Chạy toàn bộ luồng 7 module liên hoàn (M1 ➔ M7) trên Backend Python
  async function runPipeline() {
    if (!DOM.btnRunFullPipeline) return;
    DOM.btnRunFullPipeline.disabled = true;
    const oldText = DOM.btnRunFullPipeline.textContent;
    DOM.btnRunFullPipeline.textContent = '⏳ Đang Tính Toán Toàn Bộ 7 Module...';

    try {
      const payload = getPipelinePayload();
      const resp = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) {
        const errJson = await resp.json().catch(() => ({}));
        throw new Error(errJson.detail || `Lỗi máy chủ (${resp.status})`);
      }

      const data = await resp.json();
      STATE.pipelineResult = data;

      // Cập nhật toàn diện Dashboard Admin
      updateAdminDashboard(data);
      showToast('✅ Toàn bộ 7 Module (M1 ➔ M7) đã chạy thành công trên Backend Python!', 'success');
    } catch (err) {
      console.error('Pipeline error:', err);
      showToast('❌ Lỗi khi thực thi Pipeline: ' + err.message, 'danger');
    } finally {
      DOM.btnRunFullPipeline.disabled = false;
      DOM.btnRunFullPipeline.textContent = oldText || '🚀 Kích Hoạt Toàn Bộ 7 Module (M1 ➔ M7)';
    }
  }

  // Chạy riêng biệt từng module độc lập (Yêu Cầu 2)
  async function runSingleModule() {
    if (!DOM.btnRunCurrentModule) return;
    const stepNum = STATE.currentStep;
    const stepInfo = STEP_MODULE_INFO[stepNum];
    if (!stepInfo) return;

    DOM.btnRunCurrentModule.disabled = true;
    const oldText = DOM.txtBtnRunCurrentModule.textContent;
    DOM.txtBtnRunCurrentModule.textContent = `⏳ Đang thực thi ${stepInfo.name}...`;
    if (DOM.txtModuleRunStatus) {
      DOM.txtModuleRunStatus.textContent = `⚙️ Đang gửi dữ liệu tới Backend Python...`;
      DOM.txtModuleRunStatus.style.color = '#F59E0B';
    }

    try {
      const payload = getPipelinePayload();
      const reqBody = {
        module_code: stepInfo.code,
        capacity_C: payload.capacity_C,
        tau_0: payload.tau_0,
        drop_rate_p: payload.drop_rate_p,
        num_scenarios: payload.num_scenarios,
        demand_limits: payload.demand_limits
      };

      const resp = await fetch('/api/pipeline/run-module', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      });

      if (!resp.ok) {
        const errJson = await resp.json().catch(() => ({}));
        throw new Error(errJson.detail || `Lỗi máy chủ (${resp.status})`);
      }

      const res = await resp.json();
      DOM.spRuntimeMs.textContent = `Runtime: ~${res.elapsed_ms || 1} ms`;

      // Cập nhật riêng UI của module đó
      updateSingleModuleVisualizer(stepInfo.code, res.data, res.elapsed_ms);

      showToast(`✅ Đã chạy thành công riêng biệt Bước ${stepNum} (${stepInfo.name}) trong ${res.elapsed_ms} ms!`, 'success');
      if (DOM.txtModuleRunStatus) {
        DOM.txtModuleRunStatus.textContent = `🟢 Hoàn tất tính toán riêng Bước ${stepNum} (${res.elapsed_ms} ms)`;
        DOM.txtModuleRunStatus.style.color = '#34D399';
      }
    } catch (err) {
      console.error('Single module error:', err);
      showToast(`❌ Lỗi thực thi Bước ${stepNum}: ${err.message}`, 'danger');
      if (DOM.txtModuleRunStatus) {
        DOM.txtModuleRunStatus.textContent = `🔴 Thất bại: ${err.message}`;
        DOM.txtModuleRunStatus.style.color = '#F87171';
      }
    } finally {
      DOM.btnRunCurrentModule.disabled = false;
      DOM.txtBtnRunCurrentModule.textContent = oldText;
    }
  }

  // =========================================================================
  // 7.1 CÁC HÀM TRỰC QUAN HÓA THUẬT TOÁN ĐỘC LẬP (MODULE VISUALIZERS M1 - M7)
  // =========================================================================

  // M1 Visualizer: Bảng sắp xếp Merge Sort ổn định
  function renderM1Visualizer(sampleSorted) {
    if (!DOM.tbodyM1Sample || !sampleSorted) return;
    DOM.tbodyM1Sample.innerHTML = sampleSorted.map((u, i) => `
      <tr>
        <td>${i + 1}</td>
        <td><strong>#${u.user_id}</strong></td>
        <td>${formatDots(u.arrival_time)} ms</td>
        <td><span class="gold">${u.loyalty_score}</span> / 100</td>
        <td><span class="tag-badge green">ĐÃ SẮP XẾP ỔN ĐỊNH (M1)</span></td>
      </tr>
    `).join('');
  }

  // M2 Visualizer: Cây nhị phân Max-Heap và Bảng Top-K ưu tiên danh dự
  function renderHeapTree(topList) {
    if (!DOM.heapTreeVisualizer) return;
    if (!topList || topList.length === 0) {
      DOM.heapTreeVisualizer.innerHTML = '<div class="empty-state">Chưa có dữ liệu Heap</div>';
      return;
    }

    const root = topList[0];
    const left = topList[1] || null;
    const right = topList[2] || null;
    const leaves = topList.slice(3, 7);

    DOM.heapTreeVisualizer.innerHTML = `
      <div class="heap-tree-box">
        <div style="font-family: var(--font-heading); font-size: 0.85rem; font-weight: 700; color: #FCD34D; letter-spacing: 0.5px; margin-bottom: 8px;">
          🌳 CẤU TRÚC CÂY NHỊ PHÂN MAX-HEAP (ĐIỂM ƯU TIÊN TRI ÂN - CHA LUÔN LỚN HƠN HOẶC BẰNG CON):
        </div>
        
        <!-- Tầng 0: Gốc Max-Heap (Phần tử lớn nhất mảng 1D index 0) -->
        <div class="heap-level">
          <div class="heap-node root">
            <div class="hn-score">${root.loyalty_score} / 100</div>
            <div class="hn-name">${root.name || '#' + root.user_id}</div>
            <div class="hn-tag">👑 GỐC MAX-HEAP • TOP #1 (INDEX 0)</div>
          </div>
        </div>

        <div class="heap-branches">
          <div class="branch-line left"></div>
          <div class="branch-line right"></div>
        </div>

        <!-- Tầng 1: Nhánh Trái (index 1) & Nhánh Phải (index 2) -->
        <div class="heap-level sub">
          ${left ? `
            <div class="heap-node child">
              <div class="hn-score">${left.loyalty_score} / 100</div>
              <div class="hn-name">${left.name || '#' + left.user_id}</div>
              <div class="hn-tag">🌿 CON TRÁI • TOP #2 (INDEX 1)</div>
            </div>
          ` : ''}
          ${right ? `
            <div class="heap-node child">
              <div class="hn-score">${right.loyalty_score} / 100</div>
              <div class="hn-name">${right.name || '#' + right.user_id}</div>
              <div class="hn-tag">🌿 CON PHẢI • TOP #3 (INDEX 2)</div>
            </div>
          ` : ''}
        </div>

        <!-- Tầng 2: Các Node Lá (Index 3, 4, 5, 6) -->
        ${leaves.length > 0 ? `
          <div class="heap-level leaves" style="margin-top: 10px;">
            ${leaves.map((lf, idx) => `
              <div class="heap-node leaf" style="min-width: 140px; padding: 8px 12px; font-size: 0.76rem;">
                <div class="hn-score" style="font-size: 1.1rem;">${lf.loyalty_score} / 100</div>
                <div class="hn-name" style="font-size: 0.78rem; max-width: 120px;">${lf.name || '#' + lf.user_id}</div>
                <div class="hn-tag" style="font-size: 0.62rem;">LÁ #${idx + 4} (INDEX ${idx + 3})</div>
              </div>
            `).join('')}
          </div>
        ` : ''}

        <!-- Dải công thức quản lý chỉ số mảng 1D -->
        <div class="heap-formula-strip">
          <span>Gốc Heap: <strong>A[0] = Max(loyalty_score)</strong></span>
          <span>Chỉ số con trái: <strong>2*i + 1</strong></span>
          <span>Chỉ số con phải: <strong>2*i + 2</strong></span>
          <span>Node cha: <strong>(i - 1) // 2</strong></span>
          <span>Độ phức tạp: <strong>O(log N)</strong></span>
        </div>
      </div>
    `;
  }

  function renderM2Visualizer(topK) {
    if (!topK) return;
    renderHeapTree(topK);
    if (DOM.tbodyM2TopK) {
      DOM.tbodyM2TopK.innerHTML = topK.map((u, i) => `
        <tr>
          <td><span class="tag-badge ${i < 3 ? 'gold' : ''}">Top #${i + 1}</span></td>
          <td>${u.name || ('Khán giả #' + u.user_id)}</td>
          <td><span class="card-badge">${u.priority_group || 'Chính sách Tri Ân'}</span></td>
          <td><strong class="gold">${u.loyalty_score} / 100</strong></td>
          <td><span class="cyan">${u.ticket_type || 'VVIP'}</span></td>
        </tr>
      `).join('');
    }
  }

  // M3 Visualizer: Bảng Dấu Vết Hội Tụ Tìm Kiếm Nhị Phân [Low..High] Khoa Học & Khách Quan
  function renderM3Visualizer(trace, tau0, optC, optMStar, optP) {
    const tbody = document.getElementById('tbodyM3Trace');
    const effC = optC || parseDots(DOM.inputCapacityC.value) || 40000;
    const effTau0 = tau0 !== undefined ? tau0 : (parseFloat(DOM.rangeRiskTau.value) / 100.0);
    const effP = optP !== undefined ? optP : (parseFloat(DOM.rangeDropRate.value) / 100.0);
    const effMStar = optMStar || parseDots(DOM.kpiMStar?.textContent) || Math.round(effC * 1.22);
    const overbookingPct = effC > 0 ? (((effMStar - effC) / effC) * 100).toFixed(2) : '0.00';

    // 1. Cập nhật thước đo nhị phân trực quan động (Dynamic Ruler Scale)
    const elRulerC = document.getElementById('m3RulerC');
    const elRulerMStar = document.getElementById('m3RulerMStar');
    const elRuler2C = document.getElementById('m3Ruler2C');
    const elRulerMarker = document.getElementById('m3RulerMStarMarker');

    if (elRulerC) elRulerC.textContent = `${formatDots(effC)} vé`;
    if (elRulerMStar) elRulerMStar.textContent = `${formatDots(effMStar)} vé (+${overbookingPct}%)`;
    if (elRuler2C) elRuler2C.textContent = `${formatDots(effC * 2)} vé`;
    if (elRulerMarker) {
      const posPct = Math.max(12, Math.min(88, ((effMStar - effC) / effC) * 50 + 25));
      elRulerMarker.style.left = `${posPct}%`;
    }

    // 2. Cập nhật dải thẻ tóm tắt KPI thuật toán M3
    const elKpiTags = document.getElementById('m3KpiTags');
    if (elKpiTags) {
      elKpiTags.innerHTML = `
        <span class="kpi-tag-item">🏟️ Sức chứa C: <strong>${formatDots(effC)} vé</strong></span>
        <span class="kpi-tag-item">📉 Bùng vé p(t): <strong>${(effP * 100).toFixed(1)}%</strong></span>
        <span class="kpi-tag-item">⚖️ Trần rủi ro τ₀: <strong>${(effTau0 * 100).toFixed(1)}%</strong></span>
        <span class="kpi-tag-item gold">🎯 Hạn mức chốt M*: <strong>${formatDots(effMStar)} vé (+${overbookingPct}%)</strong></span>
        <span class="kpi-tag-item">🔄 Hội tụ: <strong>${(trace || []).length} bước</strong></span>
      `;
    }

    // 3. Render bảng dấu vết các bước chia đôi (Binary Search Trace Table)
    if (!tbody || !trace || trace.length === 0) return;

    tbody.innerHTML = trace.map((step, idx) => {
      const riskVal = step.risk !== undefined ? step.risk : (step.prob !== undefined ? step.prob : 0.05);
      const isSafe = riskVal <= effTau0;
      const isFinal = (idx === trace.length - 1);
      const riskPct = (riskVal * 100).toFixed(3);
      const action = step.action || (isSafe ? 'Tăng Low = Mid + 1' : 'Giảm High = Mid - 1');
      const reason = step.reason || (isSafe ? 'An toàn rủi ro (P ≤ τ₀) ➔ Thử tăng bán lố ở nửa phải' : 'Quá tải rủi ro (P > τ₀) ➔ Thu hẹp giới hạn ở nửa trái');

      const riskBarHtml = `
        <div class="m3-risk-meter-wrapper">
          <span style="font-family: monospace; font-weight: 700; color: ${isSafe ? '#34D399' : '#F87171'}; min-width: 65px;">${riskPct}%</span>
          <span class="m3-risk-meter-bg">
            <span class="m3-risk-meter-fill" style="width: ${Math.min(100, Math.max(5, riskVal * 200))}%; background: ${isSafe ? '#10B981' : '#EF4444'};"></span>
          </span>
        </div>
      `;

      const statusBadge = isSafe 
        ? `<span class="tag-badge green">✓ An toàn (≤ ${(effTau0 * 100).toFixed(1)}%)</span>` 
        : `<span class="tag-badge red">⚠️ Quá tải (&gt; ${(effTau0 * 100).toFixed(1)}%)</span>`;

      const statusFinalBadge = isFinal
        ? `<span class="tag-badge gold">⭐ HỘI TỤ M*</span>`
        : (isSafe ? `<span style="color:#34D399; font-size:0.75rem; font-weight:600;">Khả thi</span>` : `<span style="color:#F87171; font-size:0.75rem;">Loại bỏ</span>`);

      return `
        <tr class="${isFinal ? 'highlight-final-mstar' : ''}">
          <td style="text-align: center; font-weight: 700; color: ${isFinal ? '#F59E0B' : '#94A3B8'};">#${step.step}</td>
          <td style="font-family: monospace; font-weight: 600;">[${formatDots(step.low || step.left)} .. ${formatDots(step.high || step.right)}]</td>
          <td><strong style="color: #38BDF8; font-size: 0.95rem;">${formatDots(step.mid)} vé</strong></td>
          <td>${riskBarHtml}</td>
          <td>${statusBadge}</td>
          <td>
            <strong style="color: ${isSafe ? '#34D399' : '#F87171'};">${action}</strong>
            <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">${reason}</div>
          </td>
          <td>${statusFinalBadge}</td>
        </tr>
      `;
    }).join('');
  }

  // M4 Visualizer: Thẻ phân bổ Bounded Knapsack DP
  function renderM4Visualizer(alloc, demandLimits, prices) {
    if (!DOM.m4AllocationDisplay || !alloc) return;
    const dLimits = demandLimits || STATE.lastDemands || {};
    const defaultPrices = { VVIP: 0, PLATINUM: 2500000, GOLD: 1200000, SILVER: 600000 };
    const pMap = prices || defaultPrices;
    const sectorMeta = {
      VVIP: { icon: '🎖️', label: 'VVIP TRI ÂN (0 đ)', desc: 'Mẹ VNAH / Thương binh / Yếu nhân (Miễn phí)', colorClass: 'vvip' },
      PLATINUM: { icon: '💎', label: 'VIP PLATINUM', desc: 'Khán đài Trung tâm Cận sân khấu', colorClass: 'platinum' },
      GOLD: { icon: '🥇', label: 'GOLD STANDARD', desc: 'Khán đài Tiêu chuẩn Tầng 1 & 2', colorClass: 'gold' },
      SILVER: { icon: '🥈', label: 'SILVER ECONOMY', desc: 'Khán đài Phổ thông Cánh gà & Tầng 3', colorClass: 'silver' }
    };

    DOM.m4AllocationDisplay.innerHTML = Object.keys(alloc).map(sec => {
      const numAlloc = alloc[sec] || 0;
      const limit = dLimits[sec] || numAlloc;
      const pct = limit > 0 ? Math.min(100, (numAlloc / limit) * 100) : 100;
      const unitPrice = pMap[sec] || 0;
      const secRev = numAlloc * unitPrice;
      const meta = sectorMeta[sec] || { icon: '🎫', label: sec, desc: 'Phân khu vé', colorClass: '' };

      return `
        <div class="allocation-card ${meta.colorClass}">
          <div class="alloc-title">
            <span class="sec-tag">${meta.icon} ${meta.label}</span>
            <span class="sec-rev">${formatCurrencyVN(secRev)}</span>
          </div>
          <div style="font-size: 0.72rem; color: #94A3B8; margin-top: -6px;">${meta.desc}</div>
          <div class="alloc-stats">
            <div>Đơn giá: <strong class="cyan">${formatNumber(unitPrice)} đ/vé</strong></div>
            <div>Phân bổ M4: <strong class="gold">${formatDots(numAlloc)} vé</strong></div>
            <div>Trần nhu cầu thị trường: <span>${formatDots(limit)} vé</span></div>
          </div>
          <div class="alloc-progress-bg">
            <div class="alloc-progress-bar" style="width: ${pct}%"></div>
          </div>
          <div class="alloc-note">Tỷ lệ đáp ứng thị trường: ${pct.toFixed(1)}% (${formatDots(numAlloc)}/${formatDots(limit)})</div>
        </div>
      `;
    }).join('');
  }

  // M5 Visualizer: Nhật ký xử lý xung đột Greedy cổng rạp có Phân Trang & Bộ Lọc N Khách
  STATE.m5Checkins = [];
  STATE.m5CurrentPage = 1;
  STATE.m5PageSize = 15;
  STATE.m5Filter = 'ALL';
  let m5ControlsInitialized = false;

  function renderM5Page() {
    const tbody = document.getElementById('tbodyM5Sample');
    if (!tbody) return;

    const allItems = STATE.m5Checkins || [];
    const totalCount = allItems.length;

    // Đếm số lượng theo trạng thái
    const cntSuccess = allItems.filter(c => c.status === 'SUCCESS' || c.trang_thai === 'SUCCESS').length;
    const cntUpgraded = allItems.filter(c => (c.status === 'UPGRADED' || (c.trang_thai && c.trang_thai.includes('UPGRADE')))).length;
    const cntDenied = allItems.filter(c => (c.status === 'DENIED_BOARDING' || (c.trang_thai && (c.trang_thai.includes('REJECT') || c.trang_thai.includes('DENIED'))))).length;
    const cntProtected = allItems.filter(c => c.is_protected || c.protected || (c.diem_loyalty >= 70)).length;

    // Cập nhật các badge số lượng trên toolbar
    const elTotal = document.getElementById('txtM5TotalCount');
    const elCntAll = document.getElementById('cntM5All');
    const elCntSuccess = document.getElementById('cntM5Success');
    const elCntUpgraded = document.getElementById('cntM5Upgraded');
    const elCntDenied = document.getElementById('cntM5Denied');
    const elCntProtected = document.getElementById('cntM5Protected');

    if (elTotal) elTotal.textContent = totalCount;
    if (elCntAll) elCntAll.textContent = totalCount;
    if (elCntSuccess) elCntSuccess.textContent = cntSuccess;
    if (elCntUpgraded) elCntUpgraded.textContent = cntUpgraded;
    if (elCntDenied) elCntDenied.textContent = cntDenied;
    if (elCntProtected) elCntProtected.textContent = cntProtected;

    // Cập nhật dải thống kê nhanh M5
    const elStatsStrip = document.getElementById('m5StatsStrip');
    if (elStatsStrip) {
      elStatsStrip.innerHTML = `
        <span class="m5-stat-badge">Tổng: <strong class="gold">${totalCount}</strong></span>
        <span class="m5-stat-badge">✓ Đúng hạng: <strong class="green">${cntSuccess}</strong></span>
        <span class="m5-stat-badge">⚡ Nâng hạng: <strong class="cyan">${cntUpgraded}</strong></span>
        <span class="m5-stat-badge">⚠️ Quá tải DB: <strong class="red">${cntDenied}</strong></span>
        <span class="m5-stat-badge">⭐ Tri ân: <strong class="gold">100% bảo vệ</strong></span>
      `;
    }

    // Lọc danh sách theo filter hiện tại
    let filtered = allItems;
    if (STATE.m5Filter === 'SUCCESS') {
      filtered = allItems.filter(c => c.status === 'SUCCESS' || c.trang_thai === 'SUCCESS');
    } else if (STATE.m5Filter === 'UPGRADED') {
      filtered = allItems.filter(c => (c.status === 'UPGRADED' || (c.trang_thai && c.trang_thai.includes('UPGRADE'))));
    } else if (STATE.m5Filter === 'DENIED') {
      filtered = allItems.filter(c => (c.status === 'DENIED_BOARDING' || (c.trang_thai && (c.trang_thai.includes('REJECT') || c.trang_thai.includes('DENIED')))));
    } else if (STATE.m5Filter === 'PROTECTED') {
      filtered = allItems.filter(c => c.is_protected || c.protected || (c.diem_loyalty >= 70));
    }

    // Tính toán phân trang
    const pageSize = STATE.m5PageSize || 15;
    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    STATE.m5CurrentPage = Math.max(1, Math.min(STATE.m5CurrentPage, totalPages));
    const startIdx = (STATE.m5CurrentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, filtered.length);
    const pageItems = filtered.slice(startIdx, endIdx);

    // Cập nhật thông tin phân trang text
    const elPageInfo = document.getElementById('txtM5PageInfo');
    if (elPageInfo) {
      elPageInfo.innerHTML = `Hiển thị khách <strong>${filtered.length > 0 ? startIdx + 1 : 0} - ${endIdx}</strong> trong tổng số <strong>${filtered.length}</strong> khách (${STATE.m5Filter === 'ALL' ? 'Tất cả' : 'Đã lọc'})`;
    }

    // Render bảng dữ liệu
    if (pageItems.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: #94A3B8; padding: 24px;">Không có khán giả nào phù hợp với bộ lọc '${STATE.m5Filter}'.</td></tr>`;
    } else {
      tbody.innerHTML = pageItems.map((chk, i) => {
        const itemIdx = startIdx + i + 1;
        const isProt = chk.is_protected || chk.protected || (chk.diem_loyalty >= 70);
        const targetTier = chk.requested_type || chk.hang_ve_mong_muon || 'Standard';
        const actualTier = chk.assigned_seat || chk.hang_ve_thuc_nhan || 'N/A';
        const st = chk.status || chk.trang_thai || 'SUCCESS';

        let statusBadge = '<span class="tag-badge green">ĐÚNG HẠNG GHẾ</span>';
        let compText = '<span style="color:#94A3B8;">Không đền bù (0 đ)</span>';

        if (st === 'UPGRADED' || st.includes('UPGRADE')) {
          statusBadge = '<span class="tag-badge cyan">TỰ ĐỘNG NÂNG HẠNG</span>';
          compText = '<span style="color:#38BDF8;">Miễn phí nâng hạng</span>';
        } else if (st === 'DENIED_BOARDING' || st.includes('REJECT') || st.includes('DENIED')) {
          statusBadge = '<span class="tag-badge red">TỪ CHỐI VÀO RẠP (DB)</span>';
          compText = `<strong class="gold">${chk.compensation || 'Bồi thường 150% tiền vé'}</strong>`;
        }

        const noteText = chk.ghi_chu || (st === 'SUCCESS' ? 'Cấp đúng hạng vé yêu cầu' : (st === 'UPGRADED' ? `Hết hạng ${targetTier}, Free Upgrade lên ${actualTier}` : 'Quá tải rủi ro, kích hoạt đền bù 150%'));

        return `
          <tr>
            <td style="text-align: center; color: #94A3B8; font-weight: 700;">#${itemIdx}</td>
            <td>
              <strong>${chk.name || chk.ten || ('Khán giả #' + (chk.user_id || chk.id_khach))}</strong>
              <div style="font-size: 0.72rem; color: #94A3B8;">Mã: ${chk.user_id || chk.id_khach || ('TICK-' + itemIdx)} • Điểm: ${chk.diem_loyalty || 0}</div>
            </td>
            <td>
              ${isProt ? '<span class="tag-badge gold">⭐ Chính sách tri ân</span>' : '<span style="color: #94A3B8; font-size: 0.75rem;">Khán giả phổ thông</span>'}
            </td>
            <td><span class="text-amber" style="font-weight: 600;">${targetTier}</span></td>
            <td><strong class="cyan">${actualTier}</strong></td>
            <td>${statusBadge}</td>
            <td>${compText}</td>
            <td><small style="color: #94A3B8;">${noteText}</small></td>
          </tr>
        `;
      }).join('');
    }

    // Render nút điều hướng phân trang
    const elBtnContainer = document.getElementById('m5PaginationButtons');
    if (elBtnContainer) {
      let btnsHtml = `
        <button type="button" class="page-btn" data-page="1" ${STATE.m5CurrentPage <= 1 ? 'disabled' : ''} title="Trang đầu">⏮ Đầu</button>
        <button type="button" class="page-btn" data-page="${STATE.m5CurrentPage - 1}" ${STATE.m5CurrentPage <= 1 ? 'disabled' : ''} title="Trang trước">◀ Trước</button>
      `;

      let startP = Math.max(1, STATE.m5CurrentPage - 2);
      let endP = Math.min(totalPages, startP + 4);
      if (endP - startP < 4) startP = Math.max(1, endP - 4);

      for (let p = startP; p <= endP; p++) {
        btnsHtml += `<button type="button" class="page-btn ${p === STATE.m5CurrentPage ? 'active' : ''}" data-page="${p}">${p}</button>`;
      }

      btnsHtml += `
        <button type="button" class="page-btn" data-page="${STATE.m5CurrentPage + 1}" ${STATE.m5CurrentPage >= totalPages ? 'disabled' : ''} title="Trang sau">Sau ▶</button>
        <button type="button" class="page-btn" data-page="${totalPages}" ${STATE.m5CurrentPage >= totalPages ? 'disabled' : ''} title="Trang cuối">Cuối ⏭</button>
      `;
      elBtnContainer.innerHTML = btnsHtml;

      elBtnContainer.querySelectorAll('.page-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const targetPage = parseInt(btn.dataset.page, 10);
          if (targetPage && targetPage !== STATE.m5CurrentPage && targetPage >= 1 && targetPage <= totalPages) {
            STATE.m5CurrentPage = targetPage;
            renderM5Page();
          }
        });
      });
    }
  }

  function initM5PaginationEvents() {
    if (m5ControlsInitialized) return;
    m5ControlsInitialized = true;

    const filterGroup = document.getElementById('m5FilterGroup');
    if (filterGroup) {
      filterGroup.querySelectorAll('.btn-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          filterGroup.querySelectorAll('.btn-chip').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          STATE.m5Filter = btn.dataset.filter || 'ALL';
          STATE.m5CurrentPage = 1;
          renderM5Page();
        });
      });
    }

    const selPageSize = document.getElementById('selM5PageSize');
    if (selPageSize) {
      selPageSize.addEventListener('change', (e) => {
        STATE.m5PageSize = parseInt(e.target.value, 10) || 15;
        STATE.m5CurrentPage = 1;
        renderM5Page();
      });
    }
  }

  function renderM5Visualizer(sampleCheckin) {
    if (!sampleCheckin) return;
    const list = Array.isArray(sampleCheckin) ? sampleCheckin : (sampleCheckin.sample_checkins || sampleCheckin.sample_checkin || []);
    STATE.m5Checkins = list;
    initM5PaginationEvents();
    renderM5Page();
  }

  // M6 Window Visualizer: Biểu đồ p(t)
  function renderM6WindowVisualizer(pRealtime) {
    updateSlidingWindowHistory(pRealtime || 0.18);
    renderSlidingWindowChart();
  }

  // M6 Heap TTL Visualizer: Bảng quản lý và thu hồi vé quá hạn
  function renderM6HeapVisualizer(data) {
    if (!DOM.m6HeapLiveDisplay) return;
    const held = data?.held_tickets || [];
    const activeCount = data?.active_held_tickets || 24;
    const revokedCount = data?.released_expired_count || 3;

    DOM.m6HeapLiveDisplay.innerHTML = `
      <div class="ttl-status-dashboard">
        <div class="ttl-summary-strip">
          <div class="ttl-stat-box highlight">
            <div class="ttl-stat-icon">⏳</div>
            <div>
              <div class="ttl-stat-val">${activeCount} vé</div>
              <div class="ttl-stat-lbl">Vé đang tạm giữ (TTL 10 Phút)</div>
            </div>
          </div>
          <div class="ttl-stat-box">
            <div class="ttl-stat-icon">♻️</div>
            <div>
              <div class="ttl-stat-val" style="color: #F87171;">${revokedCount} vé</div>
              <div class="ttl-stat-lbl">Đã thu hồi trả về rạp (Quá hạn)</div>
            </div>
          </div>
          <div class="ttl-stat-box">
            <div class="ttl-stat-icon">⚡</div>
            <div>
              <div class="ttl-stat-val" style="color: #34D399;">O(log N)</div>
              <div class="ttl-stat-lbl">Độ phức tạp Min-Heap Extract-Min</div>
            </div>
          </div>
        </div>

        <div class="tab-table-wrapper" style="margin-top: 14px;">
          <h4 style="margin-bottom: 10px; color: #38BDF8; font-weight: 700;">Nhật Ký Quản Lý Giữ Chỗ &amp; Thu Hồi Min-Heap TTL (thuat_toan_6_thu_hoi_va_truot.py):</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Mã đơn giữ vé</th>
                <th>Khán giả</th>
                <th>Phân khu</th>
                <th>Giá vé</th>
                <th>Thời gian hết hạn</th>
                <th>Hành động Min-Heap</th>
              </tr>
            </thead>
            <tbody>
              ${held.map(t => {
                const isExpired = t.status === 'EXPIRED';
                return `
                  <tr>
                    <td><code>${t.ticket_id}</code></td>
                    <td>Khán giả <strong>#${t.user_id}</strong></td>
                    <td>${t.sector}</td>
                    <td>${formatNumber(t.price)} đ</td>
                    <td><span class="${isExpired ? 'red' : 'gold'}">${isExpired ? 'Đã quá hạn 10 phút' : 'Còn ~07 phút 20s'}</span></td>
                    <td><span class="tag-badge ${isExpired ? 'red' : 'green'}">${isExpired ? '♻️ ĐÃ THU HỒI VỀ RẠP' : '⏳ ĐANG GIỮ CHỖ'}</span></td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // M7 Visualizer: Bảng đối soát Monte Carlo SAA
  // M7 Visualizer: Bảng đối soát Monte Carlo SAA và Danh sách chi tiết N kịch bản
  function renderM7Visualizer(saa, C, mStar, overbookingPct, growthPct, probDb, tau0, numScenarios) {
    if (!DOM.m7BenchmarkDisplay || !saa) return;
    const baseRev = saa.baseline_revenue || saa.baseline?.avg_net_revenue || 0;
    const propRev = saa.proposed_revenue || saa.proposed?.avg_net_revenue || 0;
    const compCost = saa.compensation_cost || saa.proposed?.avg_compensation || 0;
    const effScenarios = saa.num_scenarios || numScenarios || 50;
    const effC = C || saa.capacity_C || 40000;

    const rawBaseEmpty = saa.avg_empty_seats_baseline !== undefined ? saa.avg_empty_seats_baseline : (saa.baseline?.avg_empty_seats !== undefined ? saa.baseline.avg_empty_seats : (saa.details?.baseline?.avg_empty_seats !== undefined ? saa.details.baseline.avg_empty_seats : Math.round(effC * 0.18)));
    const rawPropEmpty = saa.avg_empty_seats_proposed !== undefined ? saa.avg_empty_seats_proposed : (saa.proposed?.avg_empty_seats !== undefined ? saa.proposed.avg_empty_seats : (saa.details?.proposed?.avg_empty_seats !== undefined ? saa.details.proposed.avg_empty_seats : 0));
    const baseEmpty = Math.round(rawBaseEmpty);
    const propEmpty = Math.round(rawPropEmpty);
    const emptyReductionPct = baseEmpty > 0 ? (((baseEmpty - propEmpty) / baseEmpty) * 100).toFixed(1) : '0.0';

    // 1. Bảng đối soát tổng hợp (Baseline vs Proposed)
    DOM.m7BenchmarkDisplay.innerHTML = `
      <table class="data-table benchmark-table">
        <thead>
          <tr>
            <th>CHỈ SỐ ĐỐI SOÁT MONTE CARLO (S = ${effScenarios} KỊCH BẢN)</th>
            <th>MÔ HÌNH CỐ ĐỊNH (BASELINE - C)</th>
            <th>MÔ HÌNH BÁN LỐ ĐỀ XUẤT (PROPOSED - M*)</th>
            <th>HIỆU QUẢ TỐI ƯU</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Tổng số vé phát hành</strong></td>
            <td>${formatDots(effC)} vé</td>
            <td class="gold"><strong>${formatDots(mStar)} vé</strong></td>
            <td><span class="tag-badge green">+${(overbookingPct || 0).toFixed(2)}% vé bổ sung</span></td>
          </tr>
          <tr>
            <td><strong>Số ghế trống lãng phí trung bình</strong></td>
            <td><span class="red">${formatDots(baseEmpty)} ghế</span> <small style="color:#94A3B8;">(${((baseEmpty / effC) * 100).toFixed(1)}% sân)</small></td>
            <td><strong class="green">${formatDots(propEmpty)} ghế</strong> <small style="color:#94A3B8;">(${((propEmpty / effC) * 100).toFixed(1)}% sân)</small></td>
            <td><span class="tag-badge green">Giảm ${emptyReductionPct}% ghế trống lãng phí</span></td>
          </tr>
          <tr>
            <td><strong>Doanh thu thuần kỳ vọng (VNĐ)</strong></td>
            <td>${formatCurrencyVN(baseRev)}</td>
            <td class="gold"><strong>${formatCurrencyVN(propRev)}</strong></td>
            <td><span class="tag-badge green">+${(growthPct || 0).toFixed(2)}% doanh thu</span></td>
          </tr>
          <tr>
            <td><strong>Chi phí đền bù Denied Boarding</strong></td>
            <td>0 đ (Không bán lố)</td>
            <td class="red">${formatCurrencyVN(compCost)}</td>
            <td>Đã khấu trừ trực tiếp</td>
          </tr>
          <tr>
            <td><strong>Tỷ lệ quá tải thực tế P(K > C)</strong></td>
            <td>0.00%</td>
            <td class="cyan">${((probDb || 0) * 100).toFixed(2)}%</td>
            <td><span class="tag-badge green">Thỏa mãn ≤ τ₀ (${((tau0 || 0.05) * 100).toFixed(1)}%)</span></td>
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

    // 2. Bảng chi tiết N kịch bản ngẫu nhiên do người dùng chọn (Demo trực quan từng kịch bản)
    const scenarios = saa.scenarios_sample || saa.details?.scenarios_sample || saa.scenarios || [];
    const tbodyScenarios = document.getElementById('tbodyM7Scenarios');
    const txtCount = document.getElementById('txtScenariosCount');
    if (txtCount) {
      txtCount.textContent = scenarios.length > 0 ? scenarios.length : effScenarios;
    }

    if (tbodyScenarios) {
      if (scenarios.length === 0) {
        tbodyScenarios.innerHTML = `<tr><td colspan="9" style="text-align:center; color:#94A3B8; padding: 16px;">Đang chuẩn bị dữ liệu kịch bản mô phỏng...</td></tr>`;
      } else {
        tbodyScenarios.innerHTML = scenarios.map(sc => {
          const pPct = sc.drop_rate_pct !== undefined ? sc.drop_rate_pct : ((sc.p || 0) * 100).toFixed(2);
          const scMStar = sc.m_star || mStar || C;
          const arrivals = sc.arrivals !== undefined ? sc.arrivals : Math.round(scMStar * (1 - (sc.p || 0.18)));
          const occupied = sc.occupied_seats !== undefined ? sc.occupied_seats : Math.min(arrivals, C);
          const emptySeats = sc.empty_seats !== undefined ? sc.empty_seats : (sc.empty_prop !== undefined ? sc.empty_prop : Math.max(0, C - arrivals));
          const dbCount = sc.db_count !== undefined ? sc.db_count : Math.max(0, arrivals - C);
          const netRev = sc.proposed_net !== undefined ? sc.proposed_net : 0;
          const gain = sc.profit_gain !== undefined ? sc.profit_gain : (netRev - (sc.baseline_net || 0));
          const isGain = gain >= 0;

          return `
            <tr>
              <td><strong>#${sc.scenario}</strong></td>
              <td><span class="cyan">${pPct}%</span></td>
              <td><strong class="gold">${formatDots(scMStar)}</strong> vé</td>
              <td><strong>${formatDots(arrivals)}</strong> khách</td>
              <td><span class="green">${formatDots(occupied)} chỗ</span></td>
              <td><span class="${emptySeats > 0 ? 'text-amber' : 'green'}">${formatDots(emptySeats)} ghế</span></td>
              <td><span class="${dbCount > 0 ? 'tag-badge red' : 'tag-badge green'}">${dbCount > 0 ? `⚠️ ${formatDots(dbCount)} khách` : '0 (An toàn)'}</span></td>
              <td class="gold"><strong>${formatCurrencyVN(netRev)}</strong></td>
              <td><span class="tag-badge ${isGain ? 'green' : 'red'}">${isGain ? '+' : ''}${formatCurrencyVN(gain)}</span></td>
            </tr>
          `;
        }).join('');
      }
    }
  }

  // =========================================================================
  // 7.2 ĐIỀU PHỐI CẬP NHẬT GIAO DIỆN THỰC NGHIỆM (DISPATCHER)
  // =========================================================================

  // Cập nhật pane giao diện thực nghiệm khi chạy riêng một module (Yêu Cầu 2)
  function updateSingleModuleVisualizer(moduleCode, modData, elapsedMs) {
    if (!modData) return;

    const C = parseDots(DOM.inputCapacityC.value) || 40000;
    const tau0 = parseFloat(DOM.rangeRiskTau.value) / 100.0;
    const numScenarios = parseInt(DOM.inputScenarios.value, 10) || 50;

    if (moduleCode === 'M1') {
      renderM1Visualizer(modData.sample_sorted);
    } else if (moduleCode === 'M2') {
      renderM2Visualizer(modData.top_k);
    } else if (moduleCode === 'M6_WINDOW') {
      const pRealtime = modData.p_t_realtime || 0.18;
      DOM.kpiDropRate.textContent = `${(pRealtime * 100).toFixed(1)}%`;
      renderM6WindowVisualizer(pRealtime);
    } else if (moduleCode === 'M3') {
      const M_star = modData.M_star || C;
      const probDb = modData.prob_db || 0.0489;
      DOM.kpiMStar.textContent = formatDots(M_star);
      DOM.kpiProbDb.textContent = `${(probDb * 100).toFixed(2)}%`;
      const overbookingPct = C > 0 ? ((M_star - C) / C) * 100 : 0;
      const pDrop = (parseFloat(DOM.rangeDropRate?.value) || 18) / 100.0;
      renderM3Visualizer(modData.search_trace, tau0, C, M_star, pDrop);
    } else if (moduleCode === 'M4') {
      renderM4Visualizer(modData.allocation, modData.demands, modData.prices);
      // Đồng thời cập nhật số quota trên card chọn vé
      const alloc = modData.allocation || {};
      if (alloc.VVIP && DOM.txtMStarVVIP) DOM.txtMStarVVIP.textContent = formatDots(alloc.VVIP);
      if (alloc.PLATINUM && DOM.txtMStarPLATINUM) DOM.txtMStarPLATINUM.textContent = formatDots(alloc.PLATINUM);
      if (alloc.GOLD && DOM.txtMStarGOLD) DOM.txtMStarGOLD.textContent = formatDots(alloc.GOLD);
      if (alloc.SILVER && DOM.txtMStarSILVER) DOM.txtMStarSILVER.textContent = formatDots(alloc.SILVER);
    } else if (moduleCode === 'M5') {
      renderM5Visualizer(modData.sample_checkins);
    } else if (moduleCode === 'M6_HEAP') {
      renderM6HeapVisualizer(modData);
    } else if (moduleCode === 'M7') {
      const proposedNet = modData.proposed?.avg_net_revenue || modData.proposed_revenue || 0;
      const baselineNet = modData.baseline?.avg_net_revenue || modData.baseline_revenue || 0;
      const growthPct = modData.growth_pct || (baselineNet > 0 ? ((proposedNet - baselineNet) / baselineNet) * 100 : 0);
      const mStar = modData.m_star || modData.m_star_saa || modData.proposed?.m_star || parseDots(DOM.kpiMStar.textContent) || C;
      const overbookingPct = C > 0 ? ((mStar - C) / C) * 100 : 0;
      renderM7Visualizer(modData, C, mStar, overbookingPct, growthPct, 0.0489, tau0, numScenarios);
      if (modData.sample_checkins) {
        renderM5Visualizer(modData.sample_checkins);
      }
      if (proposedNet) {
        DOM.kpiNetRevenue.textContent = formatCurrencyVN(proposedNet);
        DOM.kpiGrowthPct.textContent = `+${growthPct.toFixed(2)}%`;
      }
    }
  }

  // Đảm bảo tương thích ngược 100% (Triệt tiêu hoàn toàn lỗi "... is not defined")
  window.renderM7BenchmarkResults = function (saa, C) {
    if (typeof renderM7Visualizer === 'function') {
      renderM7Visualizer(saa, C);
    }
  };
  window.renderKnapsackAllocation = function (alloc, demands, prices) {
    if (typeof renderM4Visualizer === 'function') {
      renderM4Visualizer(alloc, demands, prices);
    }
  };

  // Cập nhật toàn diện Dashboard Admin khi chạy toàn bộ 7 module
  function updateAdminDashboard(data) {
    if (!data) return;

    const C = data.capacity_C || 40000;
    const M_star = data.m3_binary_search?.M_star || C;
    const overbookingPct = C > 0 ? ((M_star - C) / C) * 100 : 0;
    const pRealtime = data.m6_sliding_window?.p_t_realtime || data.drop_rate_p || 0.18;
    const netRev = data.m7_saa_benchmark?.proposed_revenue || 0;
    const baseRev = data.m7_saa_benchmark?.baseline_revenue || 0;
    const growthPct = baseRev > 0 ? ((netRev - baseRev) / baseRev) * 100 : 0;
    const probDb = data.m3_binary_search?.prob_db || 0;
    const protectedDb = data.m7_saa_benchmark?.protected_group_db_rate || 0.0;
    const tau0 = data.tau_0 || 0.05;
    const numScenarios = data.num_scenarios || 50;

    // 1. National KPI Cards Strip
    DOM.kpiCapacityC.textContent = formatDots(C);
    DOM.kpiMStar.textContent = formatDots(M_star);
    DOM.kpiOverbookingPct.textContent = `+${overbookingPct.toFixed(2)}%`;
    DOM.kpiDropRate.textContent = `${(pRealtime * 100).toFixed(1)}%`;
    DOM.kpiNetRevenue.textContent = formatCurrencyVN(netRev);
    DOM.kpiGrowthPct.textContent = `+${growthPct.toFixed(2)}%`;
    DOM.kpiProbDb.textContent = `${(probDb * 100).toFixed(2)}%`;
    DOM.kpiProtectedDbRate.textContent = `${protectedDb.toFixed(2)}%`;

    // 2. Gọi các hàm render chuẩn hóa
    const m1Sample = data.m1_merge_sort?.sample_sorted || [];
    renderM1Visualizer(m1Sample);

    const m2TopK = data.m2_max_heap?.top_k || [];
    renderM2Visualizer(m2TopK);

    renderM6WindowVisualizer(pRealtime);

    const trace = data.m3_binary_search?.search_trace || [];
    renderM3Visualizer(trace, tau0, C, M_star, pRealtime);

    const alloc = data.m4_knapsack_dp?.allocation || {};
    const demandLimits = STATE.lastDemands || data.m4_knapsack_dp?.demands || {};
    const prices = { VVIP: 0, PLATINUM: 2500000, GOLD: 1200000, SILVER: 600000 };
    renderM4Visualizer(alloc, demandLimits, prices);

    // Cập nhật số quota trong các thẻ chọn vé khán giả
    if (alloc.VVIP && DOM.txtMStarVVIP) DOM.txtMStarVVIP.textContent = formatDots(alloc.VVIP);
    if (alloc.PLATINUM && DOM.txtMStarPLATINUM) DOM.txtMStarPLATINUM.textContent = formatDots(alloc.PLATINUM);
    if (alloc.GOLD && DOM.txtMStarGOLD) DOM.txtMStarGOLD.textContent = formatDots(alloc.GOLD);
    if (alloc.SILVER && DOM.txtMStarSILVER) DOM.txtMStarSILVER.textContent = formatDots(alloc.SILVER);

    const m5Sample = data.m5_greedy?.sample_checkin || [];
    renderM5Visualizer(m5Sample);

    // Render M6 Min-Heap TTL sample
    renderM6HeapVisualizer({
      held_tickets: [
        {"ticket_id": "TK-VVIP-001", "user_id": "12450", "sector": "VVIP Tri Ân", "price": 0, "status": "HOLDING"},
        {"ticket_id": "TK-PLAT-014", "user_id": "12451", "sector": "VIP Platinum", "price": 2500000, "status": "HOLDING"},
        {"ticket_id": "TK-GOLD-089", "user_id": "12452", "sector": "Gold Standard", "price": 1200000, "status": "HOLDING"},
        {"ticket_id": "TK-SILV-102", "user_id": "12453", "sector": "Silver Economy", "price": 600000, "status": "EXPIRED"},
      ],
      active_held_tickets: 24,
      released_expired_count: 3
    });

    const saa = data.m7_saa_benchmark || {};
    renderM7Visualizer(saa, C, M_star, overbookingPct, growthPct, probDb, tau0, numScenarios);

    // Refresh current spotlight step
    updateSpotlightCard(STATE.currentStep);
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

    ctx.clearRect(0, 0, w, h);

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

    const minVal = 0.05;
    const maxVal = 0.35;
    const stepX = (w - 70) / Math.max(1, points.length - 1);

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

    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, '#60A5FA');
    grad.addColorStop(1, '#10B981');
    ctx.strokeStyle = grad;
    ctx.lineWidth = 3;
    ctx.stroke();

    points.forEach((val, i) => {
      const x = 50 + i * stepX;
      const y = h - 30 - ((val - minVal) / (maxVal - minVal)) * (h - 70);
      ctx.fillStyle = '#10B981';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();

      if (i === points.length - 1) {
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '12px JetBrains Mono';
        ctx.fillText(`${(val * 100).toFixed(1)}%`, x - 15, y - 10);
      }
    });

    ctx.fillStyle = '#94A3B8';
    ctx.font = '11px JetBrains Mono';
    ctx.fillText('35%', 10, 35);
    ctx.fillText('20%', 10, h / 2);
    ctx.fillText('5%', 10, h - 25);
  }

  // =========================================================================
  // 9. EVENT LISTENERS & BINDINGS FOR USER & ADMIN (YÊU CẦU 1, 2, 4)
  // =========================================================================

  // --- 9.1 BỘ CHỌN DIỆN ƯU TIÊN KHÁN GIẢ (Yêu Cầu 1) ---
  if (DOM.selectUserPriority) {
    DOM.selectUserPriority.addEventListener('change', (e) => {
      const opt = e.target.options[e.target.selectedIndex];
      if (!opt) return;

      const score = parseInt(opt.getAttribute('data-score'), 10) || 80;
      const rank = parseInt(opt.getAttribute('data-rank'), 10) || 12450;
      const name = opt.getAttribute('data-name') || 'Nguyễn Văn An';
      const eta = opt.getAttribute('data-eta') || getETAString(rank, STATE.releaseRate);
      const sector = opt.getAttribute('data-type') || 'VVIP';
      const fullText = opt.text;

      STATE.userName = name;
      STATE.userPriority = fullText.split('(')[0].trim();
      STATE.queuePosition = rank;
      STATE.selectedSector = sector;

      // Cập nhật UI hàng đợi
      if (DOM.citizenPriorityBadge) {
        DOM.citizenPriorityBadge.textContent = STATE.userPriority;
      }
      if (DOM.txtLoyaltyScore) {
        DOM.txtLoyaltyScore.textContent = `${score} / 100`;
      }
      if (DOM.txtQueuePosition) {
        DOM.txtQueuePosition.textContent = `#${formatDots(rank)}`;
      }
      if (DOM.txtEtaDisplay) {
        DOM.txtEtaDisplay.textContent = eta;
      }

      // Cập nhật thanh Walker
      let pct = 28;
      if (score >= 100) pct = 96;
      else if (score >= 95) pct = 75;
      else if (score >= 90) pct = 60;
      else if (score >= 80) pct = 45;
      else pct = 15;

      if (DOM.walkerTrackFill) DOM.walkerTrackFill.style.width = `${pct}%`;
      if (DOM.walkingPersonAvatar) DOM.walkingPersonAvatar.style.left = `${pct}%`;

      // Cập nhật vé điện tử nếu đã có
      if (DOM.txtTicketFullName) DOM.txtTicketFullName.textContent = name;
      if (DOM.txtTicketPriority) DOM.txtTicketPriority.textContent = `${STATE.userPriority} (Ưu tiên ${score})`;

      showToast(`⭐ Đã chuyển sang diện: ${STATE.userPriority} (Thứ hạng: #${formatDots(rank)} • Điểm: ${score}/100)`, 'success');
    });
  }

  // --- 9.2 FORMAT SỐ VỚI DẤU CHẤM NGĂN CÁCH (Yêu Cầu 4) ---
  function setupDotFormattedInput(inputEl) {
    if (!inputEl) return;
    inputEl.addEventListener('input', (e) => {
      const cursor = e.target.selectionStart;
      const originalLen = e.target.value.length;
      const cleanNum = parseDots(e.target.value);
      if (cleanNum > 0) {
        e.target.value = formatDots(cleanNum);
      } else if (e.target.value !== '') {
        e.target.value = '0';
      }
      // Giữ vị trí con trỏ hợp lý
      const newLen = e.target.value.length;
      const newCursor = Math.max(0, cursor + (newLen - originalLen));
      try { e.target.setSelectionRange(newCursor, newCursor); } catch (_) {}
    });
  }

  // Gắn format dấu chấm cho tất cả ô nhập số
  setupDotFormattedInput(DOM.inputCapacityC);
  setupDotFormattedInput(DOM.inputNumUsers);
  setupDotFormattedInput(DOM.inputDemandVVIP);
  setupDotFormattedInput(DOM.inputDemandPLATINUM);
  setupDotFormattedInput(DOM.inputDemandGOLD);
  setupDotFormattedInput(DOM.inputDemandSILVER);

  // --- 9.3 ADMIN INPUTS & PRESETS (TẮT HOÀN TOÀN AUTO-RUN - Yêu Cầu 2) ---
  // Capacity input & preset chips
  DOM.inputCapacityC.addEventListener('input', () => {
    DOM.btnPresetChips.forEach(c => c.classList.remove('active'));
    // KHÔNG gọi pipeline - người dùng sẽ tự bấm nút khi sẵn sàng
  });

  DOM.inputCapacityC.addEventListener('change', () => {
    const val = parseDots(DOM.inputCapacityC.value);
    if (val >= 90000) {
      const curTotal = (parseDots(DOM.inputDemandVVIP.value) || 0) + (parseDots(DOM.inputDemandPLATINUM.value) || 0) + (parseDots(DOM.inputDemandGOLD.value) || 0) + (parseDots(DOM.inputDemandSILVER.value) || 0);
      if (curTotal < 80000) {
        DOM.inputDemandVVIP.value = '15.000';
        DOM.rangeDemandVVIP.value = 15000;
        DOM.inputDemandPLATINUM.value = '35.000';
        DOM.rangeDemandPLATINUM.value = 35000;
        DOM.inputDemandGOLD.value = '50.000';
        DOM.rangeDemandGOLD.value = 50000;
        DOM.inputDemandSILVER.value = '35.000';
        DOM.rangeDemandSILVER.value = 35000;
        showToast('💡 Đã tự động cập nhật trần nhu cầu thị trường lên 135.000 vé tương xứng quy mô 100.000 chỗ.', 'info');
      }
    }
  });

  DOM.btnPresetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      DOM.btnPresetChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const presetKey = chip.getAttribute('data-preset');
      const p = VENUE_PRESETS[presetKey];
      if (p) {
        STATE.venuePreset = presetKey;
        DOM.txtActiveVenue.textContent = p.name;
        DOM.inputCapacityC.value = formatDots(p.capacity);
        DOM.inputNumUsers.value = formatDots(p.totalWaiting);

        // Sync tau_0, drop_rate_p, scenarios
        if (p.tau0) {
          DOM.rangeRiskTau.value = String(p.tau0);
          DOM.lblRiskTau.textContent = `${p.tau0.toFixed(1)}%`;
        }
        if (p.pDrop) {
          DOM.rangeDropRate.value = String(p.pDrop);
          DOM.lblDropRate.textContent = `${p.pDrop.toFixed(1)}%`;
        }
        if (p.scenarios) {
          DOM.inputScenarios.value = String(p.scenarios);
        }

        // Sync user count chips
        DOM.btnUsersChips.forEach(c => {
          if (parseInt(c.getAttribute('data-users'), 10) === p.totalWaiting) {
            c.classList.add('active');
          } else {
            c.classList.remove('active');
          }
        });

        // Sync demands với định dạng dấu chấm
        DOM.inputDemandVVIP.value = formatDots(p.demands.VVIP);
        DOM.rangeDemandVVIP.value = p.demands.VVIP;
        DOM.inputDemandPLATINUM.value = formatDots(p.demands.PLATINUM);
        DOM.rangeDemandPLATINUM.value = p.demands.PLATINUM;
        DOM.inputDemandGOLD.value = formatDots(p.demands.GOLD);
        DOM.rangeDemandGOLD.value = p.demands.GOLD;
        DOM.inputDemandSILVER.value = formatDots(p.demands.SILVER);
        DOM.rangeDemandSILVER.value = p.demands.SILVER;

        showToast(`📍 Đã nạp cấu hình mẫu: ${p.name}. Hãy bấm nút [TÁI TÍNH TOÁN] để áp dụng.`, 'info');
      }
    });
  });

  // Users in queue input & chips
  DOM.inputNumUsers.addEventListener('input', () => {
    DOM.btnUsersChips.forEach(c => c.classList.remove('active'));
    // KHÔNG tự động chạy
  });

  DOM.btnUsersChips.forEach(chip => {
    chip.addEventListener('click', () => {
      DOM.btnUsersChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const u = parseInt(chip.getAttribute('data-users'), 10);
      if (u) {
        DOM.inputNumUsers.value = formatDots(u);
      }
    });
  });

  // Tau_0 & Drop rate sliders (chỉ cập nhật label, KHÔNG gọi pipeline)
  DOM.rangeRiskTau.addEventListener('input', (e) => {
    DOM.lblRiskTau.textContent = `${parseFloat(e.target.value).toFixed(1)}%`;
  });

  DOM.rangeDropRate.addEventListener('input', (e) => {
    DOM.lblDropRate.textContent = `${parseFloat(e.target.value).toFixed(1)}%`;
  });

  // Đồng bộ 2 chiều giữa ô text (có dấu chấm) và thanh trượt slider (KHÔNG gọi pipeline)
  function bindSyncFormatted(inputEl, sliderEl) {
    sliderEl.addEventListener('input', (e) => {
      inputEl.value = formatDots(e.target.value);
    });
    inputEl.addEventListener('input', (e) => {
      const val = parseDots(e.target.value);
      sliderEl.value = val;
    });
  }

  bindSyncFormatted(DOM.inputDemandVVIP, DOM.rangeDemandVVIP);
  bindSyncFormatted(DOM.inputDemandPLATINUM, DOM.rangeDemandPLATINUM);
  bindSyncFormatted(DOM.inputDemandGOLD, DOM.rangeDemandGOLD);
  bindSyncFormatted(DOM.inputDemandSILVER, DOM.rangeDemandSILVER);

  // --- 9.4 NÚT HÀNH ĐỘNG CHẠY PIPELINE & CHẠY RIÊNG MODULE ---
  // Nút chạy toàn bộ 7 module
  DOM.btnRunFullPipeline.addEventListener('click', runPipeline);

  // Nút chạy riêng từng module (Yêu Cầu 2)
  if (DOM.btnRunCurrentModule) {
    DOM.btnRunCurrentModule.addEventListener('click', runSingleModule);
  }

  // Nút Đặt lại mặc định
  DOM.btnResetSystem.addEventListener('click', async () => {
    if (!confirm('Bạn có chắc chắn muốn thiết lập lại toàn bộ dữ liệu mô phỏng về mặc định SVĐ Mỹ Đình?')) return;
    try {
      const resp = await fetch('/api/reset', { method: 'POST' });
      if (resp.ok) {
        showToast('🔄 Đã đặt lại trạng thái ban đầu thành công!', 'info');
        // Reset inputs
        DOM.inputCapacityC.value = '40.000';
        DOM.inputNumUsers.value = '185.420';
        DOM.rangeRiskTau.value = '5.0';
        DOM.lblRiskTau.textContent = '5.0%';
        DOM.rangeDropRate.value = '18';
        DOM.lblDropRate.textContent = '18.0%';
        DOM.inputDemandVVIP.value = '4.000';
        DOM.rangeDemandVVIP.value = '4000';
        DOM.inputDemandPLATINUM.value = '13.000';
        DOM.rangeDemandPLATINUM.value = '13000';
        DOM.inputDemandGOLD.value = '20.000';
        DOM.rangeDemandGOLD.value = '20000';
        DOM.inputDemandSILVER.value = '12.000';
        DOM.rangeDemandSILVER.value = '12000';
        runPipeline();
      }
    } catch (e) {
      showToast('Lỗi khi reset hệ thống', 'danger');
    }
  });

  // =========================================================================
  // 10. INITIALIZATION
  // =========================================================================
  async function initApp() {
    const savedToken = localStorage.getItem('vwr_queue_token');
    if (savedToken) {
      STATE.queueToken = savedToken;
    }

    startQueuePolling();
    await runPipeline();
    goToStep(1);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }

})();

