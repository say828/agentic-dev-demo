package kr.elice.cyworld.domain;

/** 구매 결과 (dotori.py 의 PurchaseResult 데이터클래스 포팅). */
public final class PurchaseResult {
    public final String status;
    public final String item;
    public final int price;
    public final int balance;
    public final String orderId;
    public final boolean replay;

    public PurchaseResult(String status, String item, int price, int balance, String orderId, boolean replay) {
        this.status = status;
        this.item = item;
        this.price = price;
        this.balance = balance;
        this.orderId = orderId;
        this.replay = replay;
    }

    /** replace(self, replay=...) 와 동등: replay 만 바꾼 새 인스턴스. */
    public PurchaseResult withReplay(boolean newReplay) {
        return new PurchaseResult(status, item, price, balance, orderId, newReplay);
    }
}
