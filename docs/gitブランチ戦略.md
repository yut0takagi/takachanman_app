# gitブランチ戦略
> 作成者: 髙木悠人<br>作成日時: 2025/09/22

本リポジトリでは、以下のブランチ戦略に従います。


<a href="https://qiita.com/ucan-lab/items/371cdbaa2490817a6e2a" target="_blank" style="
  display: block;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  ">
  <strong>結局 Git のブランチ戦略ってどうすればいいの？</strong><br>
  Qiita<br>
  <small>https://qiita.com</small>
</a>


## ブランチ名の命名規則

| ブランチ名 | 備考 |
| ---- | ---- |
| main | **直PUSH禁止**<br>常にリリースできる状態に保つ |
| develop | **直PUSH禁止**<br>開発用のブランチ<br>このブランチから`feature/〇〇`へ切り出す |
| feature/〇〇 | 新しい機能開発用のブランチ<br>機能開発後、developにPRを作成し、マージする |
| hotfix/〇〇 | バグ修正や緊急時に対応するためのブランチ<br>**main**から切り出す |


