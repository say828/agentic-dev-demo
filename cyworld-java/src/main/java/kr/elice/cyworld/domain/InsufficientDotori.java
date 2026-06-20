package kr.elice.cyworld.domain;

/** 잔액 부족: 구매 거부. 멱등 캐시에 남기지 않는다. */
public class InsufficientDotori extends RuntimeException {
    public InsufficientDotori(String message) {
        super(message);
    }
}
