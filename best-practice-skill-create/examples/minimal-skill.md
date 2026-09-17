# Ví dụ: skill mức Minimal

Đa số skill dừng ở đây. Một file, không thư mục con.

```
commit-helper/
└── SKILL.md
```

```markdown
---
name: commit-helper
description: >
  Sinh commit message theo quy ước Conventional Commits của team, đọc từ diff
  đang stage. Dùng khi cần viết commit message hoặc rà soát thay đổi trước khi commit.
  Triggers: "viết commit message", "commit giúp", "diff này nên ghi gì".
disable-model-invocation: true
allowed-tools: Bash(git diff *) Bash(git status *)
---

# Commit helper

## Thay đổi hiện tại

!`git diff --staged`

## Quy trình

1. Đọc diff ở trên. Nếu rỗng, báo là chưa có gì được stage rồi dừng.
2. Xác định type: feat, fix, chore, refactor, docs, test.
3. Xác định scope theo module bị đụng nhiều nhất.
4. Viết dòng tiêu đề dưới 72 ký tự, thể mệnh lệnh, không dấu chấm cuối.
5. Thêm phần thân nếu thay đổi cần giải thích lý do.

## Định dạng output

```
type(scope): tiêu đề ngắn

- gạch đầu dòng nếu cần giải thích
```

## Giới hạn

- Không tự chạy `git commit`. Chỉ đưa message để người dùng dùng.
- Không đoán scope khi diff đụng nhiều module ngang nhau — hỏi lại.
```

Điểm đáng chú ý: `disable-model-invocation: true` vì đây là việc có side effect;
`!` inject diff thật vào context trước khi Claude đọc; `allowed-tools` khớp đúng
lệnh trong body nên không bị hỏi quyền.
