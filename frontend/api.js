/********************************************
 *  API CONFIG
 ********************************************/
const BASE_URL = "https://your-api-id.execute-api.region.amazonaws.com/prod"; // TODO: replace
const USE_MOCK = true;   // true=mock, false=real backend

/********************************************
 *  GET TOKEN / USER
 ********************************************/
function getToken() {
  return localStorage.getItem("token") || "";
}

function getUserId() {
  return localStorage.getItem("userId") || "";
}

/********************************************
 *  MOCK DATA
 ********************************************/
const mockData = {
  events: [
    {
      eventId: "evt1",
      name: "Mock Concert",
      description: "This is a mocked concert event.",
      imageUrl: "https://picsum.photos/400?random=1",
      remainingTickets: 99
    },
    {
      eventId: "evt2",
      name: "Mock NBA Game",
      description: "Mock basketball game.",
      imageUrl: "https://picsum.photos/400?random=2",
      remainingTickets: 42
    }
  ],

  eventDetail: {
    eventId: "evt1",
    name: "Mock Concert",
    description: "This is a mocked event detail page.",
    imageUrl: "https://picsum.photos/400?random=3",
    remainingTickets: 88
  },

  orders: [
    {
      orderId: "order123",
      eventId: "evt1",
      quantity: 2,
      createdAt: "2025-01-01T10:00:00Z"
    }
  ]
};

/********************************************
 *  MOCK LOGIC
 ********************************************/
async function mockGet(path) {
  console.log("[MOCK GET]", path);

  if (path === "/events") {
    return { success: true, data: mockData.events };
  }

  if (path.startsWith("/events/")) {
    return { success: true, data: mockData.eventDetail };
  }

  if (path.startsWith("/orders")) {
    return { success: true, data: mockData.orders };
  }

  return { success: false, error: "Unknown mock GET" };
}

async function mockPost(path, body) {
  console.log("[MOCK POST]", path, body);

  if (path === "/login") {
    return {
      success: true,
      data: {
        token: "mock-token-user1",
        userId: body.userId
      }
    };
  }

  if (path === "/purchase") {
    return {
      success: true,
      data: {
        orderId: "order999",
        message: "Mock purchase successful"
      }
    };
  }

  return { success: false, error: "Unknown mock POST" };
}

/********************************************
 *  REAL API LOGIC
 ********************************************/
async function realGet(path) {
  const res = await fetch(BASE_URL + path, {
    method: "GET",
    headers: { Authorization: getToken() }
  });
  return res.json();
}

async function realPost(path, body) {
  const res = await fetch(BASE_URL + path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: getToken()
    },
    body: JSON.stringify(body)
  });
  return res.json();
}

/********************************************
 *  PUBLIC API FUNCTIONS (auto-switch with USE_MOCK)
 ********************************************/
async function apiGet(path) {
  return USE_MOCK ? mockGet(path) : realGet(path);
}

async function apiPost(path, body) {
  return USE_MOCK ? mockPost(path, body) : realPost(path, body);
}