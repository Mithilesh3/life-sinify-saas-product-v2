import API from "./api";

const billingService = {
  getPlans: async () => {
    const res = await API.get("/payments/plans");
    return res.data;
  },

  getPaymentHistory: async () => {
    const res = await API.get("/payments/history");
    return res.data;
  },

  createOrder: async (planName: string) => {
    const res = await API.post("/payments/create-order", {
      plan: planName,
    });
    return res.data;
  },

  verifyPayment: async (paymentData: any) => {
    const res = await API.post("/payments/verify", paymentData);
    return res.data;
  },
};

export default billingService;